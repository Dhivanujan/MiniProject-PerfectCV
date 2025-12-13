from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client.get_database()

print(f'Connected to database: {db.name}')
print(f'\nTotal users: {db.users.count_documents({})}')
print('\nExisting users:')
for user in db.users.find({}, {'email': 1, 'username': 1, 'full_name': 1, '_id': 0}):
    print(f'  - Email: {user.get("email")}')
    if user.get('username'):
        print(f'    Username: {user.get("username")}')
    if user.get('full_name'):
        print(f'    Name: {user.get("full_name")}')
