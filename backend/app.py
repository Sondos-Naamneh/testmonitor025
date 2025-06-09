from flask import Flask, request, jsonify # jsonify can be useful for more complex responses
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
import urllib.parse
from bson import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

CORS(app) # Enable CORS

# --- MongoDB Connection ---
raw_password_mongo = "Testmonitor_2025" # Your MongoDB password
encoded_password_mongo = urllib.parse.quote_plus(raw_password_mongo)
mongo_uri = f"mongodb+srv://sondos:{encoded_password_mongo}@testmonitorcluster.usrnjit.mongodb.net/?retryWrites=true&w=majority&appName=TestMonitorCluster"

# Create a new client and connect to the server
client = None # Initialize client to None
db = None
users_collection = None
quizes_collection = None
cheating_collection = None
submissions_collection = None # New collection for submissions

try:
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    client.admin.command('ping') # Ping to confirm connection
    print("Successfully connected to MongoDB! ✅")
    db = client["TestMonitorDB"] # Use a database named TestMonitorDB
    users_collection = db["users"] # Use a collection named 'users'
    quizes_collection = db["quizes"]
    cheating_collection = db["cheating_incidents"]  # New collection for cheating incidents
    submissions_collection = db["submissions"] # Initialize the collection
except Exception as e:
    print(f"Error connecting to MongoDB: {e} ❌")
    # client, db, and users_collection will remain None as initialized

app.secret_key = 'your_secret_key' # Keep this for Flask session management if needed later

# --- Routes ---

@app.route('/login', methods=['POST'])
def login():
    if users_collection is None:
        return "database_connection_error", 500

    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return "missing_fields", 400

    user = users_collection.find_one({"email": email})

    if not user:
        return "email_not_found"
    if not check_password_hash(user["password_hash"], password):
        return "incorrect_password"

    access_token = create_access_token(identity=email)
    return jsonify({
        "status": "success",
        "access_token": access_token,
        "user": {
            "username": user["user_name"],
            "email": user["email"],
            "type": user.get("type", "user")
        }
    }), 200


@app.route('/signUp', methods=['POST'])
def signup():
    # Corrected check:
    if users_collection is None:
        return "database_connection_error", 500
    
    print(f"request form : {request.form}") # Good for debugging
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not full_name or not email or not password:
        return "missing_fields", 400

    if users_collection.find_one({"email": email}):
        return "email_exists" # Keep this consistent

    hashed_password = generate_password_hash(password)
    user_name = email.split('@')[0] # Or any other logic for username

    new_user_document = {
        "user_name": user_name,
        "full_name": full_name,
        "email": email,
        "password_hash": hashed_password, # Store the hash
        "type": "user",  # Default user type
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        users_collection.insert_one(new_user_document)
    except Exception as e:
        print(f"Error inserting user: {e}")
        return "signup_failed_db_error", 500

    return "success" # Keep this consistent

@app.route('/getQuiz', methods=['GET'])
def get_quiz():
    if quizes_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    course_name = request.args.get('course')
    if not course_name:
        return jsonify({"error": "Course name is required"}), 400

    try:
        # Fetch quizzes for the specified course
        quizzes = list(quizes_collection.find({"course": course_name}, {"_id": 0}))
        if not quizzes:
            # Return empty list if no questions found for that course
            return jsonify([]), 200
        return jsonify(quizzes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reportCheating', methods=['POST'])
def report_cheating():
    if cheating_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        data = request.get_json()
        required_fields = ['username', 'quiz_name', 'incident_type', 'timestamp']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create cheating incident document
        cheating_incident = {
            "username": data['username'],
            "quiz_name": data['quiz_name'],
            "incident_type": data['incident_type'],
            "timestamp": datetime.fromisoformat(data['timestamp']),
            "details": data.get('details', ''),
            "score": data.get('score', None)
        }

        # Insert into database
        cheating_collection.insert_one(cheating_incident)
        return jsonify({"message": "Cheating incident recorded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/getCheatingIncidents', methods=['GET'])
@jwt_required()
def get_cheating_incidents():
    current_user = get_jwt_identity()  # تجيب الإيميل الحالي من التوكن

    if cheating_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    # (اختياري) يمكنك تقييد الوصول حسب المستخدم:
    # if current_user != "admin@example.com":
    #     return jsonify({"error": "Unauthorized"}), 403

    try:
        # Get filter parameters from query string
        username = request.args.get('username')
        quiz_name = request.args.get('quiz_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Build filter
        filter_query = {}
        if username:
            filter_query['username'] = username
        if quiz_name:
            filter_query['quiz_name'] = quiz_name
        if start_date and end_date:
            filter_query['timestamp'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }

        # Fetch incidents
        incidents = list(cheating_collection.find(filter_query))
        
        # Convert datetime objects and ObjectId to strings for JSON serialization
        for incident in incidents:
            incident['_id'] = str(incident['_id'])
            incident['timestamp'] = incident['timestamp'].isoformat()

        return jsonify(incidents), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deleteIncident/<string:incident_id>', methods=['DELETE'])
@jwt_required()
def delete_incident(incident_id):
    if cheating_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Validate the ID format
        if not ObjectId.is_valid(incident_id):
            return jsonify({"error": "Invalid incident ID format"}), 400

        # Attempt to delete the incident
        result = cheating_collection.delete_one({"_id": ObjectId(incident_id)})

        if result.deleted_count == 0:
            return jsonify({"error": "Incident not found"}), 404
        
        return jsonify({"message": "Incident deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submitQuiz', methods=['POST'])
def submit_quiz():
    if submissions_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        data = request.get_json()
        required_fields = ['username', 'quiz_name', 'score']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields for submission"}), 400

        submission_document = {
            "username": data['username'],
            "quiz_name": data['quiz_name'],
            "score": data['score'],
            "submitted_at": datetime.utcnow()
        }

        submissions_collection.insert_one(submission_document)
        return jsonify({"message": "Quiz submission recorded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getSubmissions', methods=['GET'])
@jwt_required()
def get_submissions():
    if submissions_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # Simple fetch all for now, can be expanded with filters later
        submissions = list(submissions_collection.find({}))
        
        for submission in submissions:
            submission['_id'] = str(submission['_id'])
            # Convert datetime to a readable string
            submission['submitted_at'] = submission['submitted_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(submissions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/verifyToken', methods=['GET'])
@jwt_required()
def verify_token():
    current_user_email = get_jwt_identity()
    user = users_collection.find_one({"email": current_user_email})
    if not user:
        return jsonify({"valid": False}), 401
    return jsonify({
        "valid": True,
        "username": user["user_name"],
        "email": user["email"],
        "type": user.get("type", "user")
    }), 200

if __name__ == '__main__':
    app.run(debug=True)

