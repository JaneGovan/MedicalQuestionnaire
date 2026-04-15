from utils.mongo import delete_user_and_records

if __name__ == '__main__':
    user_name = 'jane008'
    delete_user_and_records(user_name)