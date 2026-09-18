import os
import requests
from dotenv import load_dotenv

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

def send_line_summary(data_list):
    if not LINE_TOKEN:
        print("กรุณาระบุ LINE_TOKEN ในไฟล์ .env")
        return False

    if not data_list:
        messages_to_send = ["📋 สรุปงาน Disconnect เก็บอุปกรณ์ (+7 วันอนาคต)\n❌ ไม่พบรายการในเขตที่กำหนด"]
    else:
        messages_to_send = []
        current_msg = f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ ({len(data_list)} รายการ)\n=============================="
        
        for idx, item in enumerate(data_list, 1):
            item_text = f"\n\n[{idx}] เขต: {item['khet']}"
            item_text += f"\n🏢 ลูกค้า: {item['customer']}"
            item_text += f"\n🏠 ที่อยู่: {item['address']}"
            item_text += f"\n📞 โทร: {item['phone']}"
            item_text += f"\n📝 เหตุผล: {item['reason']}"
            item_text += "\n------------------------------"

            # ตรวจสอบความยาว หากเกิน 4,000 ตัวอักษร ให้แยกขึ้นข้อความใหม่
            if len(current_msg) + len(item_text) > 4000:
                messages_to_send.append(current_msg)
                current_msg = f"📋 สรุปงาน Disconnect (ต่อ)\n==============================" + item_text
            else:
                current_msg += item_text
                
        messages_to_send.append(current_msg)

    # ส่งข้อความผ่าน LINE Messaging API Broadcast
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_TOKEN}'
    }

    success = True
    for msg in messages_to_send:
        payload = {'messages': [{'type': 'text', 'text': msg}]}
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"ส่งข้อความ LINE ไม่สำเร็จ Status Code: {res.status_code}")
            print(f"รายละเอียด Error: {res.text}")
            success = False

    return success