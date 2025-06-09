from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

# Connection Setup
raw_password_mongo = "Testmonitor_2025"
encoded_password_mongo = urllib.parse.quote_plus(raw_password_mongo)
mongo_uri = f"mongodb+srv://sondos:{encoded_password_mongo}@testmonitorcluster.usrnjit.mongodb.net/?retryWrites=true&w=majority&appName=TestMonitorCluster"

# Connect to MongoDB
try:
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("✅ Connected to MongoDB")

    db = client["TestMonitorDB"]
    quizes_collection = db["quizes"]

    # Clear previous entries to avoid duplicates
    quizes_collection.delete_many({})
    print("🧹 Cleared existing quiz data.")

    # Quiz data with at least 5 multiple-choice questions per course
    quizzes_by_course = {
        "ELE6576 - Network Programming": [
            {"question": "Which layer of the OSI model is responsible for routing and forwarding IP packets?", "options": ["Physical Layer", "Data Link Layer", "Network Layer", "Transport Layer"], "correct_answer": "Network Layer"},
            {"question": "What does TCP stand for?", "options": ["Transmission Control Protocol", "Technical Control Protocol", "Transfer Connection Protocol", "Transport Control Protocol"], "correct_answer": "Transmission Control Protocol"},
            {"question": "Which command is used to check network connectivity between two devices?", "options": ["ipconfig", "netstat", "ping", "tracert"], "correct_answer": "ping"},
            {"question": "What is the default port number for HTTP?", "options": ["21", "80", "443", "8080"], "correct_answer": "80"},
            {"question": "Which device operates at the Data Link layer (Layer 2)?", "options": ["Router", "Hub", "Switch", "Repeater"], "correct_answer": "Switch"},
        ],
        "ELE0442 - Encryption": [
            {"question": "Which of these is an example of an asymmetric encryption algorithm?", "options": ["AES", "DES", "Blowfish", "RSA"], "correct_answer": "RSA"},
            {"question": "What is the purpose of a digital signature?", "options": ["To encrypt the entire message", "To ensure sender identity and message integrity", "To hide the sender's IP address", "To compress the message size"], "correct_answer": "To ensure sender identity and message integrity"},
            {"question": "Hashing converts data into a fixed-size string of characters. Is this statement correct?", "options": ["True", "False"], "correct_answer": "True"},
            {"question": "A 'man-in-the-middle' attack is a form of...", "options": ["Active eavesdropping", "Passive eavesdropping", "Phishing", "Brute-force attack"], "correct_answer": "Active eavesdropping"},
            {"question": "What is SSL/TLS primarily used for?", "options": ["File storage", "Secure communication over a network", "Database management", "User authentication"], "correct_answer": "Secure communication over a network"},
        ],
        "ELE5364 - Networks protocols": [
            {"question": "What is the primary function of DNS?", "options": ["To route network traffic", "To translate domain names to IP addresses", "To secure data transmission", "To assign IP addresses to devices"], "correct_answer": "To translate domain names to IP addresses"},
            {"question": "Which protocol is stateless?", "options": ["TCP", "FTP", "HTTP", "Telnet"], "correct_answer": "HTTP"},
            {"question": "Which protocol is used for sending email from a client to a server?", "options": ["POP3", "IMAP", "SMTP", "HTTP"], "correct_answer": "SMTP"},
            {"question": "What does DHCP stand for?", "options": ["Dynamic Host Configuration Protocol", "Dynamic Host Communication Protocol", "Digital Host Control Protocol", "Distributed Host Configuration Protocol"], "correct_answer": "Dynamic Host Configuration Protocol"},
            {"question": "Is UDP a connection-oriented protocol?", "options": ["Yes", "No"], "correct_answer": "No"},
        ],
        "ELE53687 - Cyber Security": [
            {"question": "What type of malware is designed to look like a legitimate program?", "options": ["Worm", "Spyware", "Trojan Horse", "Ransomware"], "correct_answer": "Trojan Horse"},
            {"question": "What is phishing?", "options": ["A type of firewall", "A method of network scanning", "A social engineering attack to steal user data", "A type of encryption"], "correct_answer": "A social engineering attack to steal user data"},
            {"question": "A network security device that monitors and filters traffic is called a...", "options": ["Router", "Switch", "Firewall", "Modem"], "correct_answer": "Firewall"},
            {"question": "What is the main purpose of multi-factor authentication (MFA)?", "options": ["To speed up login times", "To add an extra layer of security", "To store passwords", "To block cookies"], "correct_answer": "To add an extra layer of security"},
            {"question": "A 'zero-day' vulnerability is one that is...", "options": ["Not yet discovered", "Known to the public", "Known to the vendor but not yet patched", "Patched on the same day it is found"], "correct_answer": "Known to the vendor but not yet patched"},
        ]
    }

    # Insert the new quiz data with course information
    all_quizzes = []
    for course, questions in quizzes_by_course.items():
        for q in questions:
            # Add the 'course' field to each question document
            q['course'] = course
            all_quizzes.append(q)

    if all_quizzes:
        quizes_collection.insert_many(all_quizzes)
        print(f"✅ Inserted {len(all_quizzes)} new multiple-choice questions for {len(quizzes_by_course)} courses.")
    else:
        print("⚠️ No quiz data was inserted.")

except Exception as e:
    print(f"❌ Error connecting to MongoDB or inserting data: {e}")
