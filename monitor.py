import requests
import os
import json

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
SCHEDULE_ID = os.environ['SCHEDULE_ID']
FACILITY_ID = os.environ['FACILITY_ID']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
TARGET_DATE = "2026-07-31"

BASE_URL = "https://ais.usvisa-info.com/en-it/niv"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_dates():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://ais.usvisa-info.com/",
    })
    # Get login page for token
    r = session.get(f"{BASE_URL}/users/sign_in")
    print(f"Login page status: {r.status_code}")
    
    # Extract authenticity token
    token = ""
    for line in r.text.split('\n'):
        if 'authenticity_token' in line and 'value=' in line:
            try:
                token = line.split('value="')[1].split('"')[0]
                break
            except:
                continue
    print(f"Token found: {bool(token)}")
    
    # Login
    login_r = session.post(f"{BASE_URL}/users/sign_in", data={
        "user[email]": USERNAME,
        "user[password]": PASSWORD,
        "authenticity_token": token,
        "policy_confirmed": "1",
        "commit": "Sign In"
    }, allow_redirects=True)
    print(f"Login status: {login_r.status_code}")
    print(f"Login URL after redirect: {login_r.url}")
    
    # Get dates
    dates_url = f"{BASE_URL}/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false"
    r2 = session.get(dates_url, headers={
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"{BASE_URL}/schedule/{SCHEDULE_ID}/appointment"
    })
    print(f"Dates status: {r2.status_code}")
    print(f"Dates response: {r2.text[:200]}")
    return r2.json()

try:
    dates = get_dates()
    print(f"Dates received: {dates}")
    if dates and isinstance(dates, list) and len(dates) > 0:
        earliest = dates[0]['date']
        print(f"最早可用日期: {earliest}")
        if earliest < TARGET_DATE:
            send_telegram(f"🚨 美签有更早的号！\n日期: {earliest}\n快去抢: https://ais.usvisa-info.com/en-it/niv/schedule/{SCHEDULE_ID}/appointment")
        else:
            print(f"暂无更早日期，最早: {earliest}")
    else:
        print(f"未获取到日期列表，返回内容: {dates}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
