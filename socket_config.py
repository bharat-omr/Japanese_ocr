from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")  # ✅ Ensure it's initialized here
