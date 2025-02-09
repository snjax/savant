import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, cast
from flask import Flask, jsonify, request, session, send_file
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from google.oauth2 import id_token
from google.auth.transport import requests
import docker
from docker.types import Mount
from docker import errors as docker_errors
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import threading
import time
import logging
from werkzeug.datastructures import FileStorage
import atexit
from concurrent.futures import ThreadPoolExecutor
import queue

load_dotenv()

MAX_CONCURRENT_REQUESTS = 3
MAX_REQUESTS_PER_USER = 3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = mongo_client.get_database('savant')
users_collection = db.get_collection('users')
requests_collection = db.get_collection('requests')
requests_collection.create_index([('status', 1), ('createdAt', 1)])
requests_collection.create_index([('userId', 1), ('createdAt', -1)])
requests_collection.create_index([('userId', 1), ('status', 1), ('createdAt', -1)])
requests_collection.create_index([('status', 1), ('createdAt', -1)])
requests_collection.create_index([('createdAt', -1)])

# Global variables for background processing
processing_thread = None
should_stop = threading.Event()
processing_lock = threading.Lock()
request_queue = queue.Queue()
thread_pool = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)
active_requests = 0

def stream_container_logs(container, log_file_path: str):
    """Stream container logs to a file in real-time"""
    try:
        with open(log_file_path, 'wb') as f:
            # Stream and write logs in chunks
            for chunk in container.logs(stream=True, follow=True):
                f.write(chunk)
                f.flush()  # Ensure logs are written immediately
    except Exception as e:
        logger.error(f"Error streaming container logs: {e}")

def process_request(req: Dict[str, Any]):
    """Process a request using Docker"""
    logger.info(f"Starting to process request {req['id']}")
    try:
        # Ensure the request document exists in the database for upsert support in mongomock
        if requests_collection.find_one({'_id': ObjectId(req['id'])}) is None:
            new_doc = {'_id': ObjectId(req['id'])}
            requests_collection.insert_one(new_doc)
            logger.info(f"Created new document for request {req['id']}")

        requests_collection.update_one(
            {'_id': ObjectId(req['id'])},
            {'$set': {'status': 'processing'}},
            upsert=True
        )
        logger.info(f"Updated request {req['id']} status to processing")
        
        request_dir = os.path.join('requests', req['id'])
        source_file = os.path.join(request_dir, 'source.sol')
        
        # Add debug logging for paths and file existence
        abs_request_dir = os.path.abspath(request_dir)
        abs_source_file = os.path.abspath(source_file)
        logger.info(f"Local request directory: {abs_request_dir}")
        logger.info(f"Source file path: {abs_source_file}")
        logger.info(f"Source file exists: {os.path.exists(abs_source_file)}")
        if os.path.exists(abs_source_file):
            logger.info(f"Source file size: {os.path.getsize(abs_source_file)} bytes")
            logger.info(f"Source file permissions: {oct(os.stat(abs_source_file).st_mode)[-3:]}")
        
        logger.info(f"Starting Docker container for request {req['id']}")
        
        mount = Mount(
            target='/data',
            source='app_requests_data',  # Use the Docker Compose volume name
            type='volume',
            read_only=False
        )
        
        
        agent_container = os.getenv('AGENT_CONTAINER')
        ai_api_key = os.getenv('AI_API_KEY')

        if not agent_container or not ai_api_key:
            logger.info("Using dummy container")
            # This is random nonsense to pad the logs
            command = '''sh -c '
                for i in $(seq 1 20)
                do
                    echo "Echo $i"
                    sleep 1
                done
            ' '''.format(req["id"])
            
            container = get_docker_client().containers.run(
                'alpine:latest',
                command=command,
                mounts=[mount],
                detach=True,
            )
        else:
            logger.info(f"Using agent container {agent_container}")
            environment = {
                'AI_API_KEY': ai_api_key,
                'AI_MODEL': 'deepseek/deepseek-r1',
                'AI_MODEL2': 'openai/o3-mini',
                'AI_BASE_URL': 'https://openrouter.ai/api/v1',
            }
            
            command = f'''sh -c '
                uv run src/main.py /data/{req['id']}/source.sol --output /data/{req['id']}/report.pdf
            ' '''
            logger.info(f"Using command: {command}")

            container = get_docker_client().containers.run(
                agent_container,
                command=command,
                mounts=[mount],
                environment=environment,
                detach=True,
            )

        try:
            logger.info(f"Waiting for container to complete for request {req['id']}")
            
            # Stream logs in real-time
            log_file = os.path.join(request_dir, 'output.log')
            stream_container_logs(container, log_file)
            
            # Get the final result
            result = container.wait()
            
            new_status = 'completed' if result['StatusCode'] == 0 else 'failed'
            logger.info(f"Request {req['id']} completed with status {new_status}")
            requests_collection.update_one(
                {'_id': ObjectId(req['id'])},
                {'$set': {
                    'status': new_status,
                    'finishedAt': datetime.now(timezone.utc)
                }},
                upsert=True
            )
        finally:
            try:
                container.remove(force=True)
                logger.info(f"Cleaned up container for request {req['id']}")
            except Exception as e:
                logger.error(f"Failed to remove container for request {req['id']}: {e}")

    except Exception as e:
        logger.error(f"Error processing request {req['id']}: {e}", exc_info=True)
        with open(os.path.join(request_dir, 'output.log'), 'w') as f:
            f.write(f'Error: {str(e)}')
        requests_collection.update_one(
            {'_id': ObjectId(req['id'])},
            {'$set': {
                'status': 'failed',
                'finishedAt': datetime.now(timezone.utc)
            }},
            upsert=True
        )

def background_worker():
    """Background worker that processes requests from the queue"""
    global should_stop, active_requests
    logger.info("Background worker started")
    
    while not should_stop.is_set():
        try:
            # Check for pending requests in the database
            with processing_lock:
                if active_requests >= MAX_CONCURRENT_REQUESTS:
                    logger.debug("Maximum concurrent requests reached, waiting...")
                    time.sleep(1)
                    continue
                
                pending_request = requests_collection.find_one(
                    {'status': 'pending'},
                    sort=[('createdAt', 1)]  # Process oldest first
                )

                if pending_request:
                    logger.info(f"Found pending request: {pending_request['_id']}")
                    pending_request['id'] = str(pending_request['_id'])
                    active_requests += 1
                    
                    def process_and_cleanup(req):
                        global active_requests
                        try:
                            process_request(req)
                        finally:
                            with processing_lock:
                                active_requests -= 1
                    
                    thread_pool.submit(process_and_cleanup, pending_request)
                else:
                    logger.debug("No pending requests found, waiting...")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Error in background worker: {e}", exc_info=True)
            time.sleep(1)

def start_background_worker():
    """Start the background worker thread"""
    global processing_thread, should_stop, active_requests
    logger.info("Starting background worker thread")
    should_stop.clear()
    active_requests = 0
    if processing_thread is None or not processing_thread.is_alive():
        processing_thread = threading.Thread(target=background_worker, daemon=True)
        processing_thread.start()
        logger.info("Background worker thread started")
    else:
        logger.warning("Background worker thread already running")

def stop_background_worker():
    """Stop the background worker thread"""
    global should_stop, thread_pool
    logger.info("Stopping background worker thread")
    should_stop.set()
    if processing_thread:
        processing_thread.join(timeout=5)
        logger.info("Background worker thread stopped")
    thread_pool.shutdown(wait=True)
    logger.info("Thread pool shut down")

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'https://savant.chat'  # type: ignore

# Start background worker when the app is created
start_background_worker()

# Register cleanup handler
atexit.register(stop_background_worker)

_docker_client = None

def get_docker_client():
    global _docker_client
    if _docker_client is None:
        logger.info("Initializing Docker client")
        # Check common Docker socket locations
        socket_locations = [
            '/var/run/docker.sock',  # Linux
            '~/.docker/run/docker.sock',  # macOS
            '~/.docker/desktop/docker.sock',  # newer macOS Docker Desktop
        ]
        
        for socket in socket_locations:
            expanded_socket = os.path.expanduser(socket)
            logger.debug(f"Checking Docker socket at: {expanded_socket}")
            if os.path.exists(expanded_socket):
                try:
                    logger.info(f"Found Docker socket at: {expanded_socket}")
                    _docker_client = docker.DockerClient(
                        base_url=f'unix://{expanded_socket}',
                        version='auto'
                    )
                    # Test the connection
                    _docker_client.ping()
                    logger.info("Docker client initialized successfully")
                    return _docker_client
                except Exception as e:
                    logger.error(f"Failed to connect to Docker at {expanded_socket}: {e}")
                    continue
                
        error_msg = "Docker socket not found in any of the expected locations"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return _docker_client

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
        
    active_requests = requests_collection.count_documents({
        'userId': current_user.id,
        'status': {'$in': ['pending', 'processing', 'completed']}
    })
        
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'picture': user_data.get('picture'),
        'activeRequests': active_requests,
        'maxRequests': MAX_REQUESTS_PER_USER,
        'remainingRequests': max(0, MAX_REQUESTS_PER_USER - active_requests)
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

def check_user_request_limit(user_id: str) -> bool:
    active_requests = requests_collection.count_documents({
        'userId': user_id,
        'status': {'$in': ['pending', 'processing', 'completed']}
    })

    return active_requests < MAX_REQUESTS_PER_USER

@app.route('/api/v1/requests', methods=['GET', 'PUT'])
def requests_handler():
    if request.method == 'GET':
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        user_id = request.args.get('user_id')

        query = {}
        if status:
            query['status'] = status
        if user_id:
            query['userId'] = user_id

        requests = list(requests_collection.find(query).sort('createdAt', -1).skip(offset).limit(limit))
        for req in requests:
            req['id'] = str(req.pop('_id'))

        return jsonify(requests)

    # PUT request - create new request
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401

    if not check_user_request_limit(current_user.id):
        return jsonify({'error': f'Request limit reached. Maximum {MAX_REQUESTS_PER_USER} requests allowed per user.'}), 429

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not isinstance(file, FileStorage):
        return jsonify({'error': 'Invalid file'}), 400
        
    filename = file.filename
    if not filename or not filename.endswith('.sol'):
        return jsonify({'error': 'Invalid file type'}), 400

    # Read and check file content length
    file_content = file.read().decode('utf-8')
    if len(file_content) > 60 * 50:
        return jsonify({'error': 'File is too large. Maximum size is 3000 characters.'}), 400
    file.seek(0)

    new_request = {
        '_id': ObjectId(),
        'userId': current_user.id,
        'status': 'pending',
        'createdAt': datetime.now(timezone.utc),
        'fileName': filename
    }

    request_id = str(new_request['_id'])
    request_dir = os.path.join('requests', request_id)
    logger.info(f"Creating request directory: {os.path.abspath(request_dir)}")
    # TODO: Probably not the best way, but I'm tired of fixing permissions
    old_mask = os.umask(0o000)
    os.makedirs(request_dir, exist_ok=True, mode=0o777)
    os.chmod(request_dir, 0o777)
    os.umask(old_mask)

    file_path = os.path.join(request_dir, 'source.sol')
    logger.info(f"Saving file to: {os.path.abspath(file_path)}")
    file.save(file_path)
    
    # Verify file was saved
    if os.path.exists(file_path):
        logger.info(f"File saved successfully. Size: {os.path.getsize(file_path)} bytes")
    else:
        logger.error("File was not saved successfully")

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

@app.route('/api/v1/requests/<request_id>/source')
def get_request_source(request_id: str):
    try:
        request = requests_collection.find_one({'_id': ObjectId(request_id)})
        if not request:
            return jsonify({'error': 'Request not found'}), 404
            
        # # Check if user has access to this request
        # if request['userId'] != current_user.id:
        #     return jsonify({'error': 'Unauthorized'}), 403
            
        source_file = os.path.join('requests', request_id, 'source.sol')
        if os.path.exists(source_file):
            with open(source_file, 'r') as f:
                return f.read()
        return jsonify({'error': 'Source file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/requests/<request_id>/report')
def get_request_report(request_id: str):
    try:
        request = requests_collection.find_one({'_id': ObjectId(request_id)})
        if not request:
            return jsonify({'error': 'Request not found'}), 404
            
        # # Check if user has access to this request
        # if request['userId'] != current_user.id:
        #     return jsonify({'error': 'Unauthorized'}), 403
            
        report_file = os.path.join('requests', request_id, 'report.pdf')
        if os.path.exists(report_file):
            return send_file(
                report_file,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{request['fileName']}_report.pdf"
            )
        return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('requests', exist_ok=True)
    try:
        app.run(debug=True)
    finally:
        stop_background_worker() 
