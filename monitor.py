import requests
import os

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
SCHEDULE_ID = os.environ['SCHEDULE_ID']
FACILITY_ID = os.environ['FACILITY_ID']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
TARGET_DATE = "2026-07-31"  # 只要早于这个日期就通知

BASE_URL = "https://ais.usvisa-info.com/en-it/niv"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_dates():
    session = requests.Session()
    session.headers.update(HEADERS)
    # Login
    r = session.get(f"{BASE_URL}/users/sign_in")
    token = r.text.split('authenticity_token" value="')[1].split('"')[0]
    session.post(f"{BASE_URL}/users/sign_in", data={
        "user[email]": USERNAME,
        "user[password]": PASSWORD,
        "authenticity_token": token,
        "policy_confirmed": "1",
        "commit": "Sign In"
    })
    # Get dates
    r = session.get(
        f"{BASE_URL}/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false",
        headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
    )
    return r.json()

try:
    dates = get_dates()
    if dates:
        earliest = dates[0]['date']
        print(f"最早可用日期: {earliest}")
        if earliest < TARGET_DATE:
            send_telegram(f"🚨 美签有更早的号！\n日期: {earliest}\n快去抢: https://ais.usvisa-info.com/en-it/niv/schedule/{SCHEDULE_ID}/appointment")
        else:
            print(f"暂无更早日期，最早: {earliest}")
    else:
        print("未获取到日期")
except Exception as e:
    print(f"Error: {e}")
