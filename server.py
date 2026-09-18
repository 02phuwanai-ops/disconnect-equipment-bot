import os
import threading
from flask import Flask, request, abort
import requests
from dotenv import load_dotenv

from downloader import download_report
from processor import process_disconnect_data
from line_notifier import send_line_summary

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

app = Flask(__name__)

# ฟังก์ชันรันงานหลังบ้านเพื่อไม่ให้ LINE Webhook มีปัญหา Timeout
def process_and_reply():
    try:
        print("1. สั่งรันดาวน์โหลดรายงาน...")
        file_path = download_report()
        
        print("2. กรองข้อมูล...")
        data_list = process_disconnect_data(file_path)
        
        print("3. ส่งสรุปเข้า LINE...")
        send_line_summary(data_list)
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_json()
    
    events = body.get('events', [])
    for event in events:
        if event.get('type') == 'message':
            message_type = event.get('message', {}).get('type')
            text = event.get('message', {}).get('text', '').strip()
            
            # ตรวจสอบคำสั่งที่พิมพ์เข้ามาใน LINE
            if message_type == 'text' and text in ['!disconnect', '!งานยกเลิก', '!สรุปงาน']:
                print(f"ได้รับคำสั่ง: {text} กำลังเริ่มทำงาน...")
                
                # ส่งข้อความแจ้งเตือนเบื้องต้นว่ากำลังดึงข้อมูล
                reply_token = event.get('replyToken')
                reply_text(reply_token, "⏳ รับคำสั่งแล้ว กำลังดึงข้อมูลจากระบบ Gateway True กรุณารอสักครู่...")
                
                # รันสคริปต์ดึงข้อมูลใน Thread แยก
                threading.Thread(target=process_and_reply).start()

    return 'OK', 200

def reply_text(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_TOKEN}'
    }
    payload = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}]
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    # ติดตั้ง Flask ด้วยคำสั่ง: pip install flask
    app.run(port=5000)