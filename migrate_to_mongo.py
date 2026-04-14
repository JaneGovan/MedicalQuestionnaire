"""
一次性迁移脚本：将 uploads/users.json 和 uploads/records.json 导入 MongoDB

用法：
    python migrate_to_mongo.py

前置条件：
    1. MongoDB 已安装并运行在 localhost:27017
    2. pip install pymongo 已安装
"""

import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = 'medical_questionnaire'


def migrate():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # 迁移 users.json
    try:
        with open('./uploads/users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        for username, user_data in users.items():
            db.users.update_one(
                {'_id': username},
                {'$set': user_data},
                upsert=True
            )
        print(f'[OK] users: 已迁移 {len(users)} 条用户记录')
    except FileNotFoundError:
        print('[SKIP] uploads/users.json 不存在，跳过')
    except Exception as e:
        print(f'[ERROR] users 迁移失败: {e}')

    # 迁移 records.json
    try:
        with open('./uploads/records.json', 'r', encoding='utf-8') as f:
            records = json.load(f)
        for username, record_data in records.items():
            db.records.update_one(
                {'_id': username},
                {'$set': record_data},
                upsert=True
            )
        print(f'[OK] records: 已迁移 {len(records)} 条用户记录')
    except FileNotFoundError:
        print('[SKIP] uploads/records.json 不存在，跳过')
    except Exception as e:
        print(f'[ERROR] records 迁移失败: {e}')

    # # 创建索引
    # db.users.create_index('_id', unique=True)
    # db.records.create_index('_id', unique=True)
    # print('[OK] 索引创建完成')

    client.close()
    print('迁移完成！')


if __name__ == '__main__':
    migrate()
