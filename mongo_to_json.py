"""
将 MongoDB 中的数据导出回 JSON 文件：uploads/users.json 和 uploads/records.json

用法：
    python mongo_to_json.py
"""

import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
print(MONGO_URI)
DB_NAME = 'medical_questionnaire'


def export_to_json():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    os.makedirs('./uploads', exist_ok=True)

    # 导出 users
    users = {}
    for doc in db.users.find():
        username = doc.pop('_id')
        users[username] = doc
    with open('./uploads/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f'[OK] users: 已导出 {len(users)} 条用户记录 -> uploads/users.json')

    # 导出 records
    records = {}
    for doc in db.records.find():
        username = doc.pop('_id')
        records[username] = doc
    with open('./uploads/records.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f'[OK] records: 已导出 {len(records)} 条用户记录 -> uploads/records.json')

    client.close()
    print('导出完成！')


if __name__ == '__main__':
    export_to_json()
