from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_from_directory
import json
import os
import uuid
import traceback
from services.login_service import hash_with_salt, verify_password
from utils.log import Logger, Config, USER_ID, REQUEST_ID
from utils.mongo import load_all_users, load_all_records, insert_user as db_insert_user
from functools import wraps
from services.record_service import get_page_info, init_record, get_current_page_id, get_num_pages, update_record, update_time


app = Flask(__name__, static_url_path='/assets', static_folder='assets')
app.secret_key = 'medical-questionaire'



try:
    USER_MAP = load_all_users()
except:
    USER_MAP = {}
Logger.info(f'用户表：{USER_MAP}')

@app.before_request
def setup_context():
    # 2. 在请求进入时设置值
    # set() 会返回一个 Token，必须保存它以便后续还原
    u_token = USER_ID.set(session.get('user_id'))
    r_token = REQUEST_ID.set(str(uuid.uuid4()))
    
    # 将 Token 存入 Flask 的 request 对象中，方便在 teardown 时取出
    request._cv_tokens = (u_token, r_token)

@app.teardown_request
def cleanup_context(exception=None):
    # 3. 在请求结束（无论成功或失败）时重置
    # 这一步非常重要，防止线程复用导致的数据泄露
    tokens = getattr(request, '_cv_tokens', None)
    if tokens:
        u_token, r_token = tokens
        USER_ID.reset(u_token)
        REQUEST_ID.reset(r_token)

def login_required(view):
    @wraps(view)
    def wrapped(**kwargs):
        user_id = session.get('user_id')
        if not user_id or user_id not in USER_MAP:               # ① 没登录
            return redirect(url_for('index'))   # ② 滚回首页
        return view(**kwargs)                  # ③ 已登录 → 正常执行
    return wrapped

@app.errorhandler(404)
def page_not_found(e):
    Logger.warning(f'404 页面不存在: {request.path}')
    return "404, 页面不存在！", 404

@app.errorhandler(Exception)
def error_handler(e):
    Logger.error(f'{traceback.format_exc()}')
    print(traceback.format_exc())
    return "504, 服务器异常！", 500

@app.route('/', methods=['GET'])
def index():
    if session.get('user_id') and session['user_id'] in USER_MAP:
        return redirect(url_for('interact'))
    return render_template('login.html')

@app.route('/finished', methods=['GET'])
@login_required
def finish():
    user_id = session.get('user_id')
    user_records = load_all_records()
    user_record = user_records[user_id]
    non_finished_cases = user_record['non_finished_cases']
    if len(non_finished_cases) == 0:
        del session['user_id']
        return render_template('end.html')
    else:
        return redirect(url_for('interact'))

@app.route('/interact', methods=['GET'])
@login_required
def interact():
    user_id = session.get('user_id')
    current_page_id = request.args.get('page')
    user_records = load_all_records()
    user_record = user_records[user_id]
    page_list = user_records[user_id].get('case_list')
    num_pages = len(page_list)
    is_finished = user_record['is_finished']
    if not current_page_id or int(current_page_id) < 1 or int(current_page_id) > num_pages:
        page_id = get_current_page_id(user_id)
    else:
        page_id = int(current_page_id)
    return render_template(f'medwithai.html', user_id=user_id, page=page_id, num_pages=num_pages, finished=is_finished)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    if not username:
        return redirect('/?error=昵称不能为空！')
    if username in USER_MAP:
        return redirect('/?error=该昵称已注册，请更换昵称！')
    else:
        Logger.info(f'新用户 {username} 进行注册')
        pwd = request.form.get('password')
        if not pwd:
            return redirect('/?error=密码不能为空！')
        if  len(pwd) > 20:
            return redirect('/?error=密码长度不能超过20！')
        company = request.form.get('company')
        department = request.form.get('department')
        profess_title = request.form.get('prof_title')
        experience = request.form.get('experience')
        if not company or department == 'null' or profess_title == 'null' or experience == 'null':
            return redirect('/?error=请完善信息，完成新用户注册！')
        new_user_info = {
            'password': hash_with_salt(pwd),
            'company': company,
            'department': department,
            'profess_title': profess_title,
            'experience': experience
        }
        USER_MAP[username] = new_user_info
        try:
            init_record(username)
            db_insert_user(username, new_user_info)
        except:
            Logger.info(f'信息未保存，新用户 {username} 注册失败! ')
            return redirect('/?error=系统繁忙，请重新注册！')
        session['user_id'] = username
        print(username)
        Logger.info(f'新用户 {username} 注册成功! 机构：{company} 部门：{department} 职称：{profess_title} 经验：{experience}')
        return redirect(url_for('interact'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if not username:
        return redirect('/?error=昵称不能为空！')
    if username not in USER_MAP:
        return redirect('/?error=该昵称的用户不存在，请正确输入用户昵称！')
    else:
        Logger.info(f'用户 {username} 进行登录')
        input_pwd = request.form.get('password')
        if not input_pwd:
            return redirect('/?error=密码不能为空！')
        real_encoded_pwd = USER_MAP[username]['password']
        if not verify_password(input_pwd, real_encoded_pwd):
            Logger.warning(f'用户 {username} 输入密码错误')
            return redirect('/?error=密码错误，请正确输入密码！')
        else:
            session['user_id'] = username
            print(username)
            Logger.info(f'用户 {username} 登录成功')
            return redirect(url_for('interact'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'db', 'images')
@app.route('/images/<path:filename>', methods=['GET'])
@login_required
def serve_img(filename):
    return send_from_directory(IMAGE_DIR, filename)


@app.route('/checks', methods=['POST'])
@login_required
def check():
    user_id = session.get('user_id')
    data = request.get_json()
    page_id = data.get('page_id')
    Logger.info(f'请求用户{user_id}页面{page_id}的数据')
    check_data = get_page_info(user_id, int(page_id))
    Logger.info(f'页面{page_id}的数据：{check_data}')
    return jsonify(check_data)


@app.route('/records', methods=['POST'])
@login_required
def record():
    user_id = session.get('user_id')
    data = request.get_json()
    page_id = data.get('page_id')
    selected_data = data.get('selected')
    Logger.info(f'用户{user_id}页面{page_id}的提交数据: {selected_data}')
    update_record(user_id, page_id, selected_data)
    return jsonify(selected_data)

@app.route('/time', methods=['POST'])
@login_required
def time():
    user_id = session.get('user_id')
    data = request.get_json()
    page_id = data.get('page_id')
    selected_data = data.get('during_time')
    update_time(user_id, page_id, selected_data)
    Logger.info(f'更新用户{user_id}页面{page_id}的时间: {selected_data}')
    return jsonify(selected_data)


if __name__ == "__main__":
    app.run('0.0.0.0', Config['port'], debug=True, use_reloader=False)
