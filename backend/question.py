from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse
from datetime import datetime


# MongoDB connection setup
raw_password_mongo = "Testmonitor_2025"
encoded_password_mongo = urllib.parse.quote_plus(raw_password_mongo)
mongo_uri = f"mongodb+srv://sondos:{encoded_password_mongo}@testmonitorcluster.usrnjit.mongodb.net/?retryWrites=true&w=majority&appName=TestMonitorCluster"

try:
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")

    db = client["TestMonitorDB"]
    quizes_collection = db["quizes"]

    # Sample short answer network questions
    network_questions = [
        {
            "topic": "Networking",
            "question": "What does the acronym 'IP' stand for?",
            "answer_type": "short_answer",
            "correct_answer": "Internet Protocol",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "topic": "Networking",
            "question": "Which protocol is used to assign IP addresses automatically to devices?",
            "answer_type": "short_answer",
            "correct_answer": "DHCP",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "topic": "Networking",
            "question": "What is the default port number for HTTP?",
            "answer_type": "short_answer",
            "correct_answer": "80",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "topic": "Networking",
            "question": "Name a command used to check connectivity between two computers on a network.",
            "answer_type": "short_answer",
            "correct_answer": "ping",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "topic": "Networking",
            "question": "What device directs traffic between different networks?",
            "answer_type": "short_answer",
            "correct_answer": "Router",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    result = quizes_collection.insert_many(network_questions)
    print(f"✅ Inserted {len(result.inserted_ids)} questions into 'quizes' collection.")

except Exception as e:
    print(f"❌ Error: {e}")
