import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_TOKEN = os.getenv("LINE_TOKEN")


def _build_messages(data_list):
    """
    สร้างข้อความ LINE จากข้อมูลที่ processor.py ส่งมา
    คง Logic เดิมของการสรุปงานไว้ และเพิ่มเบอร์โทรที่มีอยู่ในข้อมูล
    """
    if not data_list:
        messages_to_send = [
            "📋 สรุปงาน Disconnect เก็บอุปกรณ์ (+7 วันอนาคต)\n"
            "❌ ไม่พบรายการในเขตที่กำหนด"
        ]
    else:
        messages_to_send = []
        current_msg = (
            f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ ({len(data_list)} รายการ)\n"
            "=============================="
        )

        for idx, item in enumerate(data_list, 1):
            order_id = item.get('order_id', 'N/A')
            circuit = item.get('circuit', 'N/A')
            customer = item.get('customer', 'N/A')
            address = item.get('address', 'N/A')
            phone = item.get('phone', 'N/A')
            reason = item.get('reason', 'N/A')

            item_text = f"\n\n🎫 : {order_id}"
            item_text += f"\nCircuit: {circuit}"
            item_text += f"\nลูกค้า: {customer}"
            item_text += f"\nสถานที่: {address}"
            item_text += f"\nโทร: {phone}"
            item_text += f"\n{reason}"
            item_text += "\n------------------------------"

            # LINE text message จำกัดความยาวต่อข้อความ
            if len(current_msg) + len(item_text) > 4000:
                messages_to_send.append(current_msg)
                current_msg = (
                    "📋 สรุปงาน Disconnect (ต่อ)\n"
                    "=============================="
                    + item_text
                )
            else:
                current_msg += item_text

        messages_to_send.append(current_msg)

    return messages_to_send


def send_line_summary(data_list, reply_token=None):
    """
    ส่งแบบ Reply เท่านั้น

    สำคัญ:
    - ไม่มี Push API
    - ไม่ใช้ LINE_TO
    - ต้องได้รับ reply_token จาก LINE Webhook
    - Local test ที่ไม่มี reply_token จะไม่ยิง LINE
    """
    if not LINE_TOKEN:
        print("❌ กรุณาระบุ LINE_TOKEN ในไฟล์ .env")
        return False

    if not reply_token:
        print("❌ ไม่พบ reply_token")
        print("ℹ️ ฟังก์ชันนี้รับเฉพาะการส่งแบบ Reply จาก LINE Webhook")
        print("ℹ️ Local test ไม่ควรเรียก LINE API")
        return False

    messages_to_send = _build_messages(data_list)

    # LINE Reply API เท่านั้น
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }

    # Reply API ส่งได้สูงสุด 5 messages ต่อครั้ง
    payload = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": msg}
            for msg in messages_to_send[:5]
        ]
    }

    try:
        res = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
    except requests.RequestException as e:
        print(f"❌ เชื่อมต่อ LINE Reply API ไม่สำเร็จ: {e}")
        return False

    if res.status_code != 200:
        print(
            f"❌ ส่งข้อความ LINE ผ่าน Reply ไม่สำเร็จ "
            f"Status Code: {res.status_code}"
        )
        print(f"รายละเอียด Error: {res.text}")
        return False

    print("✅ ส่งข้อความสรุปเข้า LINE สำเร็จผ่าน Reply API!")
    return True
