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

# --- เพิ่มตัวแปรสำหรับป้องกันการรันซ้อน (Lock State) ---
is_processing = False
process_lock = threading.Lock()

# ฟังก์ชันส่งข้อความ Reply กลับไปหา LINE (ใช้สำหรับกรณีแจ้ง Error ฉุกเฉิน)
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
    response = requests.post(url, headers=headers, json=payload)
    print(f"Reply Response Status: {response.status_code}, Body: {response.text}")

# ฟังก์ชันรันงานเบื้องหลัง โดยส่ง reply_token ไปใช้ตอบกลับเมื่อเสร็จสิ้น
def process_and_reply(reply_token):
    global is_processing
    try:
        print("1. สั่งรันดาวน์โหลดรายงาน...")
        file_path = download_report()
        
        print("2. กรองข้อมูล...")
        data_list = process_disconnect_data(file_path)
        
        print("3. ส่งสรุปเข้า LINE (Reply)...")
        # ส่ง reply_token เข้าไปใช้งานในฟังก์ชัน line_notifier แบบครั้งเดียวจบ
        send_line_summary(data_list, reply_token=reply_token) 
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดระหว่างประมวลผล: {e}")
        # หากเกิด Error ระหว่างทำงาน ให้ใช้ replyToken แจ้งเตือนข้อผิดพลาดกลับหาผู้ใช้
        try:
            reply_text(reply_token, f"❌ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
        except Exception as ex:
            print(f"ไม่สามารถส่งข้อความแจ้ง Error ได้: {ex}")
    finally:
        # ปลดล็อกสถานะเมื่อทำงานเสร็จสิ้น (ไม่ว่าจะสำเร็จหรือพัง)
        with process_lock:
            is_processing = False
        print("สถานะบอท: พร้อมรับคำสั่งใหม่แล้ว")

@app.route("/webhook", methods=['POST'])
def webhook():
    global is_processing
    body = request.get_json()
    
    events = body.get('events', [])
    for event in events:
        if event.get('type') == 'message':
            message_type = event.get('message', {}).get('type')
            text = event.get('message', {}).get('text', '').strip()
            
            # ตรวจสอบคำสั่ง
            if message_type == 'text' and text in ['disconnect', 'งานยกเลิก']:
                reply_token = event.get('replyToken')
                
                # ตรวจสอบและล็อกสถานะป้องกันการรันซ้อน
                with process_lock:
                    if is_processing:
                        print("ปฏิเสธคำสั่งซ้อน: บอทกำลังประมวลผลงานค้างอยู่...")
                        reply_text(reply_token, "⏳ บอทกำลังประมวลผลรายการก่อนหน้าอยู่ กรุณารอสักครู่ครับ...")
                        continue
                    
                    is_processing = True

                print(f"ได้รับคำสั่ง: {text} กำลังเริ่มทำงาน...")
                
                # 📌 หมายเหตุสำคัญ: 
                # ห้ามเรียก reply_text ที่นี่เด็ดขาด! เพราะจะทำให้ replyToken ถูกใช้และหมดอายุก่อน 
                # ที่ Playwright จะทำงานเสร็จ ให้เก็บ Token ไว้ส่งผลลัพธ์รวบยอดตอนท้ายทีเดียวครับ
                
                # รันงานทั้งหมดใน Background Thread
                threading.Thread(target=process_and_reply, args=(reply_token,)).start()

    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)