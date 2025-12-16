"""
Test MongoDB Connection and Login
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import socket

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

print("=" * 70)
print("MongoDB Connection Test")
print("=" * 70)

# Test 1: DNS Resolution
print("\n1. Testing DNS Resolution...")
try:
    hostname = MONGO_URI.split('@')[1].split('/')[0] if '@' in MONGO_URI else MONGO_URI.split('//')[1].split('/')[0]
    print(f"   Hostname: {hostname}")
    ip = socket.gethostbyname(hostname.split(':')[0])
    print(f"   ✅ DNS Resolution successful: {ip}")
except Exception as e:
    print(f"   ❌ DNS Resolution failed: {e}")
    print("\n   Possible solutions:")
    print("   - Check your internet connection")
    print("   - Try changing DNS servers (use 8.8.8.8 or 1.1.1.1)")
    print("   - Check firewall settings")
    sys.exit(1)

# Test 2: MongoDB Connection
print("\n2. Testing MongoDB Connection...")
try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=15000,
        socketTimeoutMS=15000
    )
    # Test the connection
    client.admin.command('ping')
    print("   ✅ MongoDB connection successful!")
    
    # Test 3: Database Access
    print("\n3. Testing Database Access...")
    db = client.mydatabase
    users_count = db.users.count_documents({})
    print(f"   ✅ Database accessible. Users count: {users_count}")
    
    # Test 4: Try to find a specific user
    print("\n4. Testing User Lookup...")
    test_email = "lavindunadungamuwa@gmail.com"
    user = db.users.find_one({'email': test_email})
    if user:
        print(f"   ✅ User found: {user.get('email')}")
        print(f"   User ID: {user.get('_id')}")
        print(f"   Username: {user.get('username', 'N/A')}")
    else:
        print(f"   ⚠️  User not found: {test_email}")
        print(f"\n   Available users:")
        for u in db.users.find({}, {'email': 1, 'username': 1}).limit(5):
            print(f"   - {u.get('email')} (username: {u.get('username', 'N/A')})")
    
    client.close()
    
except ServerSelectionTimeoutError as e:
    print(f"   ❌ Connection timeout: {e}")
    print("\n   Possible solutions:")
    print("   - Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0)")
    print("   - Verify MongoDB cluster is active")
    print("   - Check VPN/Firewall settings")
    sys.exit(1)
except ConnectionFailure as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All tests passed!")
print("=" * 70)
