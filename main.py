from flask import Flask
from flask_cors import CORS
from src.socket_config import socketio  # Import from socket_config.py

app = Flask(__name__)

# Enable CORS globally for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Flask-SocketIO with correct CORS settings
socketio.init_app(app, cors_allowed_origins="*")

#  Import Blueprints **AFTER** initializing Flask & socketio
from src.extract_text_with_progress_bar import extract_bp
from src.extract_text_recheck import verify_bp
from src.submit_data import submit_bp

#  Register Blueprints
app.register_blueprint(extract_bp, url_prefix="/extract")
app.register_blueprint(verify_bp, url_prefix="/verify")
app.register_blueprint(submit_bp, url_prefix="/submit")

@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Unified Flask API!"}

#  Run with WebSockets enabled
if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)




"""from flask import Flask
from flask_cors import CORS

# Import Blueprints
from main1 import extract_bp
from main2 import verify_bp
from take_data import submit_bp
#from translate import translate_bp

app = Flask(__name__)
# Allow all domains (for testing) or specify the frontend URL
CORS(app, resources={r"/*": {"origins": "*"}})
# Register Blueprints
CORS(extract_bp)
CORS(verify_bp)
CORS(submit_bp)
# Register all the Blueprints
app.register_blueprint(extract_bp, url_prefix="/extract")
app.register_blueprint(verify_bp, url_prefix="/verify")
app.register_blueprint(submit_bp, url_prefix="/submit")
#app.register_blueprint(translate_bp, url_prefix="/translate")

@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Unified Flask API!"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run on localhost:5000 """