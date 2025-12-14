"""
Create a test user in the local MongoDB database for testing.
"""
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

# Connect to local MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['perfectcv']

# Test user credentials
test_user = {
    'email': 'test@example.com',
    'password': generate_password_hash('Test123!'),  # Password: Test123!
    'full_name': 'Test User',
    'username': 'testuser',
    'created_at': datetime.utcnow()
}

# Check if user already exists
existing_user = db.users.find_one({'email': test_user['email']})

if existing_user:
    print(f"✓ User already exists: {test_user['email']}")
    print(f"  User ID: {existing_user['_id']}")
else:
    # Insert test user
    result = db.users.insert_one(test_user)
    print(f"✓ Test user created successfully!")
    print(f"  Email: {test_user['email']}")
    print(f"  Password: Test123!")
    print(f"  User ID: {result.inserted_id}")

# Show all users in database
print(f"\n📊 Total users in database: {db.users.count_documents({})}")
print("\nAll users:")
for user in db.users.find({}, {'email': 1, 'full_name': 1, 'username': 1}):
    print(f"  - {user.get('email')} ({user.get('full_name', 'N/A')})")

print("\n" + "="*60)
print("You can now login with:")
print("  Email: test@example.com")
print("  Password: Test123!")
print("="*60)
