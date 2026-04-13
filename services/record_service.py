import json
import os
import copy
import random
from utils.log import Logger
from utils.tools import retry
import threading

file_lock = threading.Lock()
RECORDS_FILE = './uploads/records.json'


def load_records():
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_records(data):
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

with open('./db/ai_reasoning.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)


# @retry()
def init_record(user_id: str):
    with file_lock:
        try:
            user_records = load_records()
        except:
            user_records = {}
        cases_ids = list(cases.keys())
        len_cases = len(cases_ids)
        front_cases_ids = copy.deepcopy(cases_ids)
        random.shuffle(cases_ids)
        random.shuffle(front_cases_ids)
        selected = [None] * len(cases_ids) * 2
        case_list = front_cases_ids + cases_ids
        for case_id in cases_ids:
            first_ai = random.choice([True, False])
            front_idx = case_list.index(case_id)
            end_idx = case_list.index(case_id, len_cases)
            selected[front_idx] = {j:"" for j in cases[case_id].get('features').keys()}
            selected[front_idx]["with_ai"] = first_ai
            selected[end_idx] = {j:"" for j in cases[case_id].get('features').keys()}
            selected[end_idx]["with_ai"] = not first_ai
            selected[front_idx]["confidence"] = ''
            selected[end_idx]["confidence"] = ''
            selected[front_idx]["during_time"] = 0
            selected[end_idx]["during_time"] = 0
            selected[front_idx]["diagnosis_result"] = ""
            selected[end_idx]["diagnosis_result"] = ""
            if first_ai:
                selected[front_idx]["assistant"] = ''
            else:
                selected[end_idx]["assistant"] = ''
        
        user_record_info = {
            "case_list": case_list,
            "current_page": 1,
            "non_finished_cases": list(range(len(case_list))),
            "selected": selected
        }
        user_records[user_id] = user_record_info
        save_records(user_records)

# @retry()
def get_page_info(user_id: str, page_idx: int):
    with file_lock:
        user_records = load_records()
        db_data = cases
        # print(user_id, db_data)
        user_record = user_records[user_id]
        case_list = user_record.get('case_list')
        selected = user_record.get('selected')
        case_id = case_list[page_idx-1]

        page_info = {
            "src_image_name": os.path.basename(db_data[case_id].get('image_path')),
            "des_image_name": os.path.basename(db_data[case_id].get('process_image')),
            "reasoning": db_data[case_id].get('reasoning'),
            "conclusion": db_data[case_id].get('conclusion'),
            "features": db_data[case_id].get('features'),
            "non_finished_cases": user_record.get('non_finished_cases'),
            "selected": selected[page_idx-1],
            'ground_truth': db_data[case_id].get('ground_truth')
        }

        return page_info

@retry()
def get_current_page_id(user_id: str):
    with file_lock:
        user_records = load_records()
        current_page_id = user_records[user_id].get('current_page')
        return current_page_id

@retry()
def get_num_pages(user_id: str):
    with file_lock:
        user_records = load_records()
        page_list = user_records[user_id].get('case_list')
        return len(page_list)


@retry()
def update_record(user_id: str, page_idx: int, selected_data: dict):
    with file_lock:
        user_records = load_records()
        user_record = user_records[user_id]
        selected = user_record.get('selected')[page_idx-1]
        user_record['current_page'] = page_idx
        is_finished_case = False
        for feat, val in selected_data.items():
            if feat in selected:
                selected[feat] = val
        for k, v in selected.items():
            if v == "":
                is_finished_case = False
                break
        else:
            is_finished_case = True
        idx_page = page_idx-1
        if is_finished_case and idx_page in set(user_record['non_finished_cases']):
            user_record['non_finished_cases'].remove(idx_page)
        save_records(user_records)

@retry()
def update_time(user_id: str, page_idx: int, time_tag: int):
    with file_lock:
        user_records = load_records()
        user_record = user_records[user_id]
        selected = user_record['selected'][page_idx-1]
        selected["during_time"] = time_tag
        save_records(user_records)



