import os
import requests
from dotenv import load_dotenv

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

def get_my_id():
    # ส่งคำสั่งขอประวัติการแชทหรือดึงข้อมูลผ่าน Messaging API
    # หรือใช้วิธีง่ายสุด: ปริ้นท์ข้อมูล bot info ออกมาเช็กว่า Token ใช้ได้จริงไหม
    url = 'https://api.line.me/v2/bot/info'
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    res = requests.get(url, headers=headers)
    print("Bot Info:", res.text)

if __name__ == "__main__":
    get_my_id()