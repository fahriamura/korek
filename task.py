import requests
import time
import threading
import subprocess
import urllib.parse
import json
import random

# URL dan headers
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://tgapp.matchain.io',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://tgapp.matchain.io/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

def parse_user_data(init_data):
    if "user=" in init_data:
        user_data_encoded = init_data.split('user=')[1].split('&')[0]
        user_data_json = urllib.parse.unquote(user_data_encoded)
        user_data = json.loads(user_data_json)
        return user_data
    return None

def get_nama_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        data = ""
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'first_name' in user_data_dict:
            data = user_data_dict['first_name']
        if 'last_name' in user_data_dict:
            data = data + " " + user_data_dict['last_name']
        if 'username' in user_data_dict:
            data = data + " " + f"({user_data_dict['username']})"
        return data
    return None

# Fungsi untuk melakukan start session
def authenticate(user_data, initdata):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/user/login'
    payload = {
        "uid": user_data["id"],
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "username": user_data.get("username", ""),
        "tg_login_params": initdata
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['data']['token']
    except requests.exceptions.RequestException as error:
        print(f'Error during authentication: {error}')
        raise

def get_tasks(user_data, token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/task/list'
    headers['Authorization'] = token
    payload = {"uid": user_data["id"]}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except json.JSONDecodeError:
        print(f"JSON Decode Error: Token Invalid")
        return []
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return []
    
def complete_task(user_data,task_name, token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/task/complete'
    headers['Authorization'] = token
    payload = {
            "uid": user_data["id"],
            "type": task_name
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except json.JSONDecodeError:
        print(f"JSON Decode Error: Token Invalid")
        return None
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None
    
def claim_task(user_data,task_name, token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/task/claim'
    headers['Authorization'] = token
    payload = {
            "uid": user_data["id"],
            "type": task_name
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except json.JSONDecodeError:
        print(f"JSON Decode Error: Token Invalid")
        return None
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None

# Fungsi untuk menjalankan operasi untuk setiap initData
def process_initdata(init_data):
    while True:
        try:
            user_data = parse_user_data(init_data)
            auth_token = authenticate(user_data, init_data)
            
            if auth_token:
                tasks = get_tasks(user_data,auth_token)
                task_list = tasks.get('data', [])
                
                for task in task_list:
                    if not task['complete']:
                        print(f"[ Task ]: Finishing task {task['name']}", end="\r", flush=True)
                        time.sleep(1)
                        complete_task_result = complete_task(user_data, task['name'], auth_token)   
                        
                        if complete_task_result:
                            result = complete_task_result.get('data', False)
                            
                            if result:
                                print(f"[ Task ]: Claiming task {task['name']}", flush=True)
                                time.sleep(1)
                                claim_task_result = claim_task(user_data, task['name'], auth_token)
                                
                                if claim_task_result:
                                    print(f"[ Task ]: Complete and Claimed {task['name']}", flush=True)
                                else:
                                    print(f"[ Task ]: Failed to claim task {task['name']}", flush=True)
                            else:
                                print(f"[ Task ]: Failed to claim task {task['name']}", flush=True)
                        else:
                            print(f"[ Task ]: Failed to finishing {task['name']}", flush=True)
            
            else:
                print("Authentication failed")
                break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            break


# Main program
def main():
    initdata_file = "initdata.txt"
    initdata_list = read_initdata_from_file(initdata_file)
    threads = []
    
    for init_data in initdata_list:
        thread = threading.Thread(target=process_initdata, args=(init_data.strip(),))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
        subprocess.run(["python3", "gamee.py"])
