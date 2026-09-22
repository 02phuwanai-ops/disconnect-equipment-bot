import os
import requests
from dotenv import load_dotenv

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

def get_latest_user():
    # ใช้ดึงโควต้าหรือตรวจสอบสถานะเพื่อคอนเฟิร์ม Token ก่อน
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    
    # เนื่องจาก LINE Messaging API ไม่มีช่องทางให้ดึงข้อความย้อนหลังตรงๆ (เพื่อความเป็นส่วนตัวและความปลอดภัย)
    # วิธีที่ง่ายและชัวร์ที่สุดในการเอา User ID ตัวจริงของคุณมาใส่ตอนนี้ มี 2 วิธีครับ:
    print("--------------------------------------------------")
    print("💡 คำแนะนำในการหา User ID ตัวจริงของคุณ:")
    print("1. เปิดไฟล์ server.py แล้วเพิ่ม print(event['source']['userId']) ไว้ในฟังก์ชันรับข้อความ")
    print("2. พิมพ์ข้อความอะไรก็ได้ใน LINE อีกครั้ง แล้วดู User ID ที่ขึ้นในหน้าจอ Terminal ของ server.py")
    print("--------------------------------------------------")

if __name__ == "__main__":
    get_latest_user()