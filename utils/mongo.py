import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = 'medical_questionnaire'

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return _get_client()[DB_NAME]


# ── users ──────────────────────────────────────────────

def find_user(username):
    doc = get_db().users.find_one({'_id': username})
    if doc:
        doc.pop('_id', None)
        return doc
    return None


def insert_user(username, user_data):
    get_db().users.insert_one({'_id': username, **user_data})


def update_user(username, user_data):
    get_db().users.update_one({'_id': username}, {'$set': user_data})


def load_all_users():
    """Return a dict like the original users.json: {username: user_data}"""
    result = {}
    for doc in get_db().users.find():
        username = doc.pop('_id')
        result[username] = doc
    
    return result


# ── records ──────────────────────────────────────────────

def find_record(username):
    doc = get_db().records.find_one({'_id': username})
    if doc:
        doc.pop('_id', None)
        return doc
    return None


def upsert_record(username, record_data):
    get_db().records.update_one(
        {'_id': username},
        {'$set': record_data},
        upsert=True
    )


def load_all_records():
    """Return a dict like the original records.json: {username: record_data}"""
    result = {}
    for doc in get_db().records.find():
        username = doc.pop('_id')
        result[username] = doc
    
    return result

