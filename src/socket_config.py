from flask_socketio import SocketIO

# Enable CORS for WebSockets
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)
