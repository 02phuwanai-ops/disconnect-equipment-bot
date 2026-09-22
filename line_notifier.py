import os
import requests
from dotenv import load_dotenv

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

def send_line_summary(data_list, reply_token=None):
    if not LINE_TOKEN:
        print("กรุณาระบุ LINE_TOKEN ในไฟล์ .env")
        return False

    if not data_list:
        messages_to_send = ["📋 สรุปงาน Disconnect เก็บอุปกรณ์ (+7 วันอนาคต)\n❌ ไม่พบรายการในเขตที่กำหนด"]
    else:
        messages_to_send = []
        current_msg = f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ ({len(data_list)} รายการ)\n=============================="
        
        for idx, item in enumerate(data_list, 1):
            order_id = item.get('order_id', 'N/A')
            circuit = item.get('circuit', 'N/A')
            customer = item.get('customer', 'N/A')
            address = item.get('address', 'N/A')
            reason = item.get('reason', 'N/A')

            # จัดรูปแบบข้อความตามสไตล์ที่ต้องการ
            item_text = f"\n\n🎫 : {order_id}"
            item_text += f"\nCircuit: {circuit} {customer} {address}"
            item_text += f"\n{reason}"
            item_text += "\n------------------------------"

            # ตรวจสอบความยาว หากเกิน 4,000 ตัวอักษร ให้แยกข้อความใหม่
            if len(current_msg) + len(item_text) > 4000:
                messages_to_send.append(current_msg)
                current_msg = f"📋 สรุปงาน Disconnect (ต่อ)\n==============================" + item_text
            else:
                current_msg += item_text
                
        messages_to_send.append(current_msg)

    success = True
    
    # ส่งข้อความผ่าน Reply API (ฟรี ไม่เสียค่าใช้จ่าย)
    if reply_token:
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_TOKEN}'
        }
        
        payload = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': msg} for msg in messages_to_send[:5]]
        }
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"ส่งข้อความ LINE ผ่าน Reply ไม่สำเร็จ Status Code: {res.status_code}")
            print(f"รายละเอียด Error: {res.text}")
            success = False
        else:
            print("✅ ส่งข้อความสรุปเข้า LINE สำเร็จผ่าน Reply API!")
    else:
        print("❌ ไม่พบ reply_token จึงไม่สามารถส่งข้อความแบบ Reply ได้")
        success = False

    return success