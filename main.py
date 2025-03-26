from flask import Flask
from flask_cors import CORS

# Import Blueprints
from main1 import extract_bp
from main2 import verify_bp
from take_data import submit_bp
#from translate import translate_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Register all the Blueprints
app.register_blueprint(extract_bp, url_prefix="/extract")
app.register_blueprint(verify_bp, url_prefix="/verify")
app.register_blueprint(submit_bp, url_prefix="/submit")
#app.register_blueprint(translate_bp, url_prefix="/translate")

@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Unified Flask API!"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run on localhost:5000
