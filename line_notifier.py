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

    success = True
    
    # บังคับใช้ Reply API เท่านั้น (ฟรี 100% ไม่ติดโควต้า 429)
    if reply_token:
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_TOKEN}'
        }
        
        # LINE Reply API ส่งได้สูงสุด 5 ข้อความต่อ 1 Request
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
        print("❌ ไม่พบ reply_token จึงไม่สามารถส่งข้อความแบบ Reply ได้ (ระวังอย่าใช้ Broadcast)")
        success = False

    return success