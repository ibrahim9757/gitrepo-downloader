# Import Flask library
from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a route (API endpoint)
@app.route('/api/message', methods=['GET'])
def hello():
    """
    This function handles GET requests to /api/message.
    When frontend calls this URL, it will get a JSON response.
    """
    response = {"message": "Hello from Backend!"}
    return jsonify(response)  # Send JSON back to frontend

@app.route('/')
def home():
    return 'Backend is running!'

# Run the backend server
if __name__ == '__main__':
    # localhost:5000 by default
    app.run(debug=True)
