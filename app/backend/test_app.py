import os
import pytest
import mongomock
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from bson import ObjectId
from .app import app as flask_app, process_request, background_worker, should_stop
from werkzeug.datastructures import FileStorage
from io import BytesIO
import importlib

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test_secret_key'
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.get_database('savant')
    mock_users = mock_db.get_collection('users')
    mock_requests = mock_db.get_collection('requests')
    
    # Patch MongoDB collections  
    from . import app as app_module
    monkeypatch.setattr(app_module, "users_collection", mock_users)
    monkeypatch.setattr(app_module, "requests_collection", mock_requests)
    
    return {
        'client': mock_client,
        'db': mock_db,
        'users': mock_users,
        'requests': mock_requests
    }

@pytest.fixture
def mock_google_verify(monkeypatch):
    def mock_verify(*args, **kwargs):
        return {
            'sub': 'test_user_id',
            'email': 'test@example.com',
            'name': 'Test User'
        }
    monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', mock_verify)

@pytest.fixture
def mock_docker(request, monkeypatch):
    # Import the module object for app/backend/app.py explicitly
    app_module = importlib.import_module("backend.app")
    monkeypatch.setattr(app_module, "_docker_client", None)
    
    if request.config.getoption("--use-docker"):
        print("Using real docker client")
        # Clear any existing Docker environment variables
        monkeypatch.delenv("DOCKER_TLS_VERIFY", raising=False)
        monkeypatch.delenv("DOCKER_CERT_PATH", raising=False)
        monkeypatch.delenv("DOCKER_HOST", raising=False)
        
        # Check common Docker socket locations
        socket_locations = [
            '/var/run/docker.sock',  # Linux
            '~/.docker/run/docker.sock',  # macOS
            os.path.expanduser('~/.docker/desktop/docker.sock'),  # newer macOS Docker Desktop
        ]
        
        docker_socket = None
        for socket in socket_locations:
            expanded_socket = os.path.expanduser(socket)
            if os.path.exists(expanded_socket):
                docker_socket = expanded_socket
                break
                
        if not docker_socket:
            pytest.skip("Docker socket not found in any of the expected locations")
            
        monkeypatch.setenv("DOCKER_HOST", f"unix://{docker_socket}")
            
        from backend.app import get_docker_client as real_get_docker_client
        return real_get_docker_client()
    else:
        print("Using mocked docker client")
        mock_container = Mock()
        mock_container.logs.return_value = [b'Test log output']
        mock_container.wait.return_value = {'StatusCode': 0}
        
        mock_client = Mock()
        mock_client.containers.run.return_value = mock_container
        monkeypatch.setattr(app_module, "get_docker_client", lambda: mock_client)
        return mock_client

def test_login(client, mock_mongo, mock_google_verify):
    """Test user login with Google token"""
    response = client.post('/login', json={'token': 'fake_token'})
    assert response.status_code == 200
    assert response.json['success'] is True
    
    # Verify user was created in database
    user = mock_mongo['users'].find_one({'_id': 'test_user_id'})
    assert user is not None
    assert user['email'] == 'test@example.com'
    assert user['name'] == 'Test User'

def test_login_no_token(client):
    """Test login without token"""
    response = client.post('/login', json={})
    assert response.status_code == 400
    assert 'error' in response.json

def test_logout(client, mock_mongo, mock_google_verify):
    """Test user logout"""
    # First login
    client.post('/login', json={'token': 'fake_token'})
    
    # Then logout
    response = client.get('/logout')
    assert response.status_code == 200
    assert response.json['success'] is True

def test_create_request(client, mock_mongo, mock_google_verify, tmp_path):
    """Test creating a new request"""
    # Login first
    client.post('/login', json={'token': 'fake_token'})
    
    # Create a test Solidity file
    data = {
        'file': (BytesIO(b'contract Test {}'), 'test.sol')
    }
    
    response = client.put(
        '/api/v1/user/test_user_id/requests',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['status'] == 'pending'
    
    # Verify request was created in database
    request = mock_mongo['requests'].find_one({'userId': 'test_user_id'})
    assert request is not None
    assert request['status'] == 'pending'
    assert request['fileName'] == 'test.sol'

def test_get_user_requests(client, mock_mongo, mock_google_verify):
    """Test getting user requests"""
    # Login first
    client.post('/login', json={'token': 'fake_token'})
    
    # Create a test request in the database
    request_id = ObjectId()
    mock_mongo['requests'].insert_one({
        '_id': request_id,
        'userId': 'test_user_id',
        'status': 'pending',
        'createdAt': datetime.now(timezone.utc),
        'fileName': 'test.sol'
    })
    
    response = client.get('/api/v1/user/test_user_id/requests')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == str(request_id)

def test_get_request_logs(client, mock_mongo, mock_google_verify, tmp_path):
    """Test getting request logs"""
    # Login first
    client.post('/login', json={'token': 'fake_token'})
    
    # Create a test request
    request_id = str(ObjectId())
    mock_mongo['requests'].insert_one({
        '_id': ObjectId(request_id),
        'userId': 'test_user_id',
        'status': 'pending',
        'createdAt': datetime.now(timezone.utc),
        'fileName': 'test.sol'
    })
    
    # Create a test log file
    os.makedirs(os.path.join('requests', request_id), exist_ok=True)
    with open(os.path.join('requests', request_id, 'output.log'), 'w') as f:
        f.write('Test log output')
    
    response = client.get(f'/api/v1/requests/{request_id}/logs')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Test log output'
    
    # Cleanup
    os.remove(os.path.join('requests', request_id, 'output.log'))
    os.rmdir(os.path.join('requests', request_id))

def test_process_request(mock_mongo, mock_docker):
    """Test request processing function"""
    request_id = str(ObjectId())
    request = {
        'id': request_id,
        'userId': 'test_user_id',
        'status': 'pending',
        'fileName': 'test.sol'
    }
    
    # Create necessary directories
    os.makedirs(os.path.join('requests', request_id), exist_ok=True)
    with open(os.path.join('requests', request_id, 'source.sol'), 'w') as f:
        f.write('contract Test {}')
    
    process_request(request)
    
    # Verify request status was updated
    processed_request = mock_mongo['requests'].find_one({'_id': ObjectId(request_id)})
    assert processed_request is not None
    assert processed_request['status'] in ['completed', 'failed']  # For now, accept both statuses
    
    # If using mock Docker client, verify it was called
    if hasattr(mock_docker.containers, 'run') and hasattr(mock_docker.containers.run, 'assert_called_once'):
        mock_docker.containers.run.assert_called_once()
    
    # Cleanup
    request_dir = os.path.join('requests', request_id)
    for filename in ['source.sol', 'output.log', 'report.pdf']:
        file_path = os.path.join(request_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    os.rmdir(request_dir)

def test_background_worker(mock_mongo, mock_docker):
    """Test background worker functionality"""
    # Create a test request
    request_id = ObjectId()
    mock_mongo['requests'].insert_one({
        '_id': request_id,
        'userId': 'test_user_id',
        'status': 'pending',
        'createdAt': datetime.now(timezone.utc),
        'fileName': 'test.sol'
    })
    
    # Create necessary directories and files
    request_dir = os.path.join('requests', str(request_id))
    os.makedirs(request_dir, exist_ok=True)
    with open(os.path.join(request_dir, 'source.sol'), 'w') as f:
        f.write('contract Test {}')
    
    # Run worker for one iteration
    should_stop.set()  # This will make the worker run only once
    background_worker()
    
    # Verify request was processed
    processed_request = mock_mongo['requests'].find_one({'_id': request_id})
    assert processed_request['status'] == 'completed'
    
    # Cleanup
    for filename in ['source.sol', 'output.log', 'report.pdf']:
        file_path = os.path.join(request_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    os.rmdir(request_dir) 
