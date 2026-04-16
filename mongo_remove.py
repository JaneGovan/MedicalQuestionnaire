from utils.mongo import delete_user_and_records
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser(description="remove user record")
    parser.add_argument("-u", "--username", default="", required=True, type=str, help="用户名，即用户ID")
    config = parser.parse_args()
    delete_user_and_records(config.username)