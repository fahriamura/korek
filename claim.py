import requests
import time
import threading
import subprocess
import urllib.parse
import json

def read_init_data_from_file(filename):
    with open(filename, 'r') as file:
        init_data_list = [line.strip() for line in file if line.strip()]
    return init_data_list

def parse_user_data(init_data):
    if "user=" in init_data:
        user_data_encoded = init_data.split('user=')[1].split('&')[0]
        user_data_json = urllib.parse.unquote(user_data_encoded)
        user_data = json.loads(user_data_json)
        return user_data
    return None

def authenticate(user_data, init_data):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/user/login'
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

    payload = {
        "uid": user_data["id"],
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "username": user_data.get("username", ""),
        "tg_login_params": init_data
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['data']['token']
    except requests.exceptions.RequestException as error:
        print(f'Error during authentication: {error}')
        raise

def get_claim(user_data, token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/reward/claim'
    headers = {
        'Authorization': token,
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {"uid": user_data["id"]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(response.text)
        start_farm(user_data, token)
    except requests.exceptions.RequestException as error:
        print(f'Claim not available: {error.response.json()["message"]}')
        start_farm(user_data, token)

def start_farm(user_data, token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/reward/farming'
    headers = {
        'Authorization': token,
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {"uid": user_data["id"]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        get_balance(user_data,token)
    except requests.exceptions.RequestException as error:
        print(f'Error during start farming: {error.response}')

def get_balance(user_data,token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/point/reward'
    headers = {
        'Authorization': token,
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    }
    payload = {"uid": user_data["id"]}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print('Balance:', response.json().get('reward'))
    except requests.exceptions.RequestException as error:
        print(f'Error fetching balance: {error}')

def process_init_data(init_data):
    while True:
        try:
            user_data = parse_user_data(init_data)
            if user_data is None:
                print(f'No user data found in init_data: {init_data}')
                break
            print(f'Name: {user_data['username']}')
            token = authenticate(user_data, init_data)
            get_claim(user_data, token)
        except Exception as e:
            print(f'An error occurred: {e}')
            print('Running claim.py...')
            subprocess.run(['python3', 'claim.py'])
            break
        except KeyboardInterrupt:
            print("\nProses dihentikan paksa oleh anda!")
            break
        print('Sleeping for 6 hours...')
        time.sleep(6 * 60 * 60)

def main():
    init_data_list = read_init_data_from_file('initdata.txt')
    threads = []
    for init_data in init_data_list:
        thread = threading.Thread(target=process_init_data, args=(init_data,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    
