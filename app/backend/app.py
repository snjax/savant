import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, cast
from flask import Flask, jsonify, request, session
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from google.oauth2 import id_token
from google.auth.transport import requests
import docker
from docker.types import Mount
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import threading
import time
from werkzeug.datastructures import FileStorage

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'https://savant.chat'  # type: ignore

_docker_client = None

def get_docker_client():
    global _docker_client
    if _docker_client is None:
        # Check common Docker socket locations
        socket_locations = [
            '/var/run/docker.sock',  # Linux
            '~/.docker/run/docker.sock',  # macOS
            os.path.expanduser('~/.docker/desktop/docker.sock'),  # newer macOS Docker Desktop
        ]
        
        for socket in socket_locations:
            expanded_socket = os.path.expanduser(socket)
            if os.path.exists(expanded_socket):
                _docker_client = docker.DockerClient(
                    base_url=f'unix://{expanded_socket}',
                    version='auto'
                )
                return _docker_client
                
        raise RuntimeError("Docker socket not found in any of the expected locations")
    return _docker_client

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = mongo_client.get_database('savant')
# TODO: Add indexes
users_collection = db.get_collection('users')
requests_collection = db.get_collection('requests')

processing_thread = None
should_stop = threading.Event()
processing_lock = threading.Lock()

def process_request(req: Dict[str, Any]):
    """Process a request using Docker"""
    try:
        # Ensure the request document exists in the database for upsert support in mongomock
        if requests_collection.find_one({'_id': ObjectId(req['id'])}) is None:
            new_doc = {'_id': ObjectId(req['id'])}
            requests_collection.insert_one(new_doc)

        requests_collection.update_one(
            {'_id': ObjectId(req['id'])},
            {'$set': {'status': 'processing'}},
            upsert=True
        )
        
        request_dir = os.path.join('requests', req['id'])
        source_file = os.path.join(request_dir, 'source.sol')
        
        # For demo purposes, use a simple container that just copies the file
        container = get_docker_client().containers.run(
            'alpine:latest',
            command='cp /data/source.sol /data/report.pdf',
            volumes={
                os.path.abspath(request_dir): {
                    'bind': '/data',
                    'mode': 'rw'
                }
            },  # type: ignore
            detach=True,
            remove=False  # Don't auto-remove so we can get logs
        )

        try:
            result = container.wait()
            
            logs = container.logs()
            with open(os.path.join(request_dir, 'output.log'), 'wb') as f:
                f.write(logs)
            
            new_status = 'completed' if result['StatusCode'] == 0 else 'failed'
            requests_collection.update_one(
                {'_id': ObjectId(req['id'])},
                {'$set': {'status': new_status}},
                upsert=True
            )
        finally:
            try:
                container.remove(force=True)
            except:
                pass  # Ignore errors during cleanup

    except Exception as e:
        with open(os.path.join(request_dir, 'output.log'), 'w') as f:
            f.write(f'Error: {str(e)}')
        requests_collection.update_one(
            {'_id': ObjectId(req['id'])},
            {'$set': {'status': 'failed'}},
            upsert=True
        )

def background_worker():
    """Background worker that processes requests from the queue"""
    global should_stop
    while True:
        try:
            # Check for pending requests in the database
            pending_request = requests_collection.find_one(
                {'status': 'pending'},
                sort=[('createdAt', 1)]  # Process oldest first
            )

            if pending_request:
                pending_request['id'] = str(pending_request['_id'])
                process_request(pending_request)
            else:
                time.sleep(1)

        except Exception as e:
            print(f"Error in background worker: {e}")
            time.sleep(1)
        if should_stop.is_set():
            break

def start_background_worker():
    """Start the background worker thread"""
    global processing_thread, should_stop
    should_stop.clear()
    if processing_thread is None or not processing_thread.is_alive():
        processing_thread = threading.Thread(target=background_worker, daemon=True)
        processing_thread.start()

def stop_background_worker():
    """Stop the background worker thread"""
    global should_stop
    should_stop.set()
    if processing_thread:
        processing_thread.join(timeout=5)

class User(UserMixin):
    def __init__(self, user_id: str, email: str, name: str):
        self.id = user_id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    user_data = users_collection.find_one({'_id': user_id})
    if not user_data:
        return None
    return User(user_id, user_data['email'], user_data['name'])

@app.route('/api/v1/user/me')
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_data = users_collection.find_one({'_id': current_user.id})
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'picture': user_data.get('picture')
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    request_json = request.get_json()
    if not request_json:
        return jsonify({'error': 'No JSON data'}), 400
        
    token = request_json.get('token')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
        
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            os.getenv('GOOGLE_CLIENT_ID')
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
            
        user_id = idinfo['sub']
        user_data = {
            'email': idinfo['email'],
            'name': idinfo.get('name', 'Unknown'),
            'picture': idinfo.get('picture'),
            'last_login': datetime.now(timezone.utc)
        }
        
        users_collection.update_one(
            {'_id': user_id},
            {'$set': user_data},
            upsert=True
        )
        
        user = User(user_id, user_data['email'], user_data['name'])
        login_user(user)
        
        return jsonify({
            'id': user_id,
            'email': user_data['email'],
            'name': user_data['name'],
            'picture': user_data.get('picture')
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/api/v1/auth/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/v1/user/<user_id>/requests', methods=['GET', 'PUT'])
@login_required
def user_requests_handler(user_id: str):
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        user_reqs = list(requests_collection.find({'userId': user_id}))
        for req in user_reqs:
            req['id'] = str(req.pop('_id'))
        return jsonify(user_reqs)

    # PUT request - create new request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not isinstance(file, FileStorage):
        return jsonify({'error': 'Invalid file'}), 400
        
    filename = file.filename
    if not filename or not filename.endswith('.sol'):
        return jsonify({'error': 'Invalid file type'}), 400

    new_request = {
        '_id': ObjectId(),
        'userId': user_id,
        'status': 'pending',
        'createdAt': datetime.now(timezone.utc),
        'fileName': filename
    }

    request_id = str(new_request['_id'])
    request_dir = os.path.join('requests', request_id)
    os.makedirs(request_dir, exist_ok=True)

    file_path = os.path.join(request_dir, 'source.sol')
    file.save(file_path)

    requests_collection.insert_one(new_request)
    new_request['id'] = request_id
    del new_request['_id']

    return jsonify(new_request)

@app.route('/api/v1/requests/<request_id>')
def get_request(request_id: str):
    try:
        req = requests_collection.find_one({'_id': ObjectId(request_id)})
        if req:
            req['id'] = str(req.pop('_id'))
            return jsonify(req)
    except:
        pass
    return jsonify({'error': 'Request not found'}), 404

@app.route('/api/v1/requests')
def get_all_requests():
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    status = request.args.get('status')

    query = {}
    if status:
        query['status'] = status

    requests = list(requests_collection.find(query).skip(offset).limit(limit))
    for req in requests:
        req['id'] = str(req.pop('_id'))

    return jsonify(requests)

# TODO: Do we need to show logs to anyone?
@app.route('/api/v1/requests/<request_id>/logs')
def get_request_logs(request_id: str):
    try:
        if requests_collection.find_one({'_id': ObjectId(request_id)}):
            log_file = os.path.join('requests', request_id, 'output.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return f.read()
            return ''
    except:
        pass
    return jsonify({'error': 'Request not found'}), 404

if __name__ == '__main__':
    os.makedirs('requests', exist_ok=True)
    start_background_worker()
    try:
        app.run(debug=True)
    finally:
        stop_background_worker() 
