import requests
import time
import threading
import subprocess
import urllib.parse
import json
import random

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

def play(token):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/game/play'
    headers['Authorization'] = token
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(response.text)
        return response.json()
    except json.JSONDecodeError:
        print(f"JSON Decode Error: Token Invalid")
        return None
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None

def claim(auth_token, game_id):
    url = 'https://tgapp-api.matchain.io/api/tgapp/v1/game/claim'
    headers['Authorization'] = auth_token
    points = random.randint(50, 100)
    json_data = {
        'game_id': game_id,
        'point': points,
    }
    try:
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f'Error during claim: {error}')
        return None

def process_init_data(init_data):
    while True:
        try:
            user_data = parse_user_data(init_data)
            auth_token = authenticate(user_data, init_data)
            
            play_response = play(auth_token)
            game_id = play_response.get('data', {}).get('game_id')
            
            if game_id:
                print(f"Game ID: {game_id}")
                time.sleep(30)
                claim_response = claim(auth_token, game_id)
                if claim_response:
                    print(f"Claim Response: {claim_response}")
                else:
                    print("Failed to claim")
            else:
                print("Failed to get game ID")
                break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            break

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
