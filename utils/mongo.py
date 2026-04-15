import os
from utils.log import Logger
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


def delete_user_and_records(username):
    db = get_db()
    if not find_user(username) and not find_record(username):
        print(f'[Warning]: 用户"{username}"信息不存在')
        Logger.info(f'用户"{username}"信息不存在')
    else:
        if find_user(username):
            db.users.delete_one({'_id': username})
            print(f'[OK] users: 已删除mongodb中用户"{username}"的记录')
            Logger.info(f'已删除users中用户"{username}"的信息')
        if find_record(username):
            db.records.delete_one({'_id': username})
            print(f'[OK] records: 已删除mongodb中用户"{username}"的记录')
            Logger.info(f'已删除records中用户"{username}"信息')

