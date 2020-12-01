import json
import os
import time
from urllib import request

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.getenv("BASE_DIR", './output_with_mentenance/')
RAW_JSON_DIR = os.getenv("RAW_JSON_DIR", "json_outputs/")
DECODE_JSON_DIR = os.getenv("DECODE_JSON_DIR", "decode_json_outputs/")
JSONLINES_DIR = os.getenv("JSONLINES_DIR", "jsonl_outputs/")
DOMAIN = os.getenv("DOMAIN")
NAME = os.getenv("NAME")
PASS = os.getenv("PASS")
API_PATH = os.getenv("API_PATH")
LOGIN_PATH = os.getenv("LOGIN_PATH")


def exec():
    # bs4でよかったかもしれない...
    res_login_page = requests.get(DOMAIN + LOGIN_PATH)
    soup = BeautifulSoup(res_login_page.text, 'html.parser')

    payload = {
        # 'utf8': '✓',
        'name': NAME,
        'pass': PASS,
        'form_build_id': soup.find('input', attrs={'name': 'form_build_id'}).get('value'),
        'form_id': soup.find('input', attrs={'name': 'form_id'}).get('value'),
        'op': soup.find('input', attrs={'name': 'op'}).get('value'),
    }

    session = requests.Session()
    session.post(DOMAIN + LOGIN_PATH, data=payload)
    res_jsonapi_page = session.get(DOMAIN + API_PATH)
    print(res_jsonapi_page.text)
    data = res_jsonapi_page.json()
    elements = []
    for link in data["links"]:
        try:
            elements.append(data["links"][link]["href"])
        except Exception:
            continue

    os.makedirs(f"{BASE_DIR}{RAW_JSON_DIR}", exist_ok=True)
    # os.makedirs(f"{BASE_DIR}{DECODE_JSON_DIR}", exist_ok=True)
    # os.makedirs(f"{BASE_DIR}{JSONLINES_DIR}", exist_ok=True)

    for url in elements:
        index = 0
        if url.startswith(DOMAIN):
            try:
                while url:
                    res = session.get(url)
                    split_url = url.split('?')
                    base_url = split_url[0]
                    suffix = base_url.split('/')[-2]
                    file_name = base_url.split('/')[-1]
                    print('url:', url)
                    content = res.json()
                    with open(f"{BASE_DIR}{RAW_JSON_DIR}{suffix}__{file_name}_{str(index).zfill(5)}.json", 'w') as f:
                        f.write(res.text)
                    # with open(f"{BASE_DIR}{DECODE_JSON_DIR}{suffix}__{file_name}_{str(index).zfill(5)}.json", 'w') as f:
                    #    json.dump(json_content, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
                    # with jsonlines.open(f'{BASE_DIR}{JSONLINES_DIR}{file_name}_{str(index).zfill(5)}.jsonl', mode='w') as f:
                    #     f.write(json_content)

                    try:
                        url = content["links"]["next"]["href"]
                        index += 1
                    except KeyError:
                        url = None

                    res.close()
            except Exception as e:
                print(e)
                print(f"Exception raised in url:{url}")
                continue


if __name__ == "__main__":
    exec()
