import requests
import os
import re

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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    })

    # Get login page
    r = session.get(f"{BASE_URL}/users/sign_in")
    print(f"Login page status: {r.status_code}")

    # Extract token with regex
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', r.text)
    if not match:
        match = re.search(r'authenticity_token[^>]+value="([^"]+)"', r.text)
    token = match.group(1) if match else ""
    print(f"Token: {token[:20] if token else 'NOT FOUND'}")

    # Login
    session.headers.update({
        "X-CSRF-Token": token,
        "Referer": f"{BASE_URL}/users/sign_in",
    })
    login_r = session.post(f"{BASE_URL}/users/sign_in", data={
        "user[email]": USERNAME,
        "user[password]": PASSWORD,
        "authenticity_token": token,
        "policy_confirmed": "1",
        "commit": "Sign In"
    })
    print(f"Login status: {login_r.status_code}, URL: {login_r.url}")

    # Get dates
    dates_url = f"{BASE_URL}/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false"
    r2 = session.get(dates_url, headers={
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"{BASE_URL}/schedule/{SCHEDULE_ID}/appointment",
    })
    print(f"Dates status: {r2.status_code}")
    print(f"Dates response: {r2.text[:300]}")
    return r2.json()

try:
    dates = get_dates()
    if dates and isinstance(dates, list) and len(dates) > 0:
        earliest = dates[0]['date']
        print(f"最早可用日期: {earliest}")
        if earliest < TARGET_DATE:
            send_telegram(f"🚨 美签有更早的号！\n日期: {earliest}\n快去抢: https://ais.usvisa-info.com/en-it/niv/schedule/{SCHEDULE_ID}/appointment")
        else:
            print(f"暂无更早日期，最早: {earliest}")
    else:
        print(f"未获取到日期: {dates}")
except Exception as e:
    import traceback
    traceback.print_exc()
