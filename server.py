import os
import threading
from flask import Flask, request
import requests
from dotenv import load_dotenv

from downloader import download_report
from processor import process_disconnect_data
from line_notifier import send_line_summary

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

app = Flask(__name__)

# --- ป้องกันการรันซ้อน (Logic เดิม) ---
is_processing = False
process_lock = threading.Lock()


def reply_text(reply_token, text):
    """
    Reply ฉุกเฉินกลับไปยัง LINE
    ใช้ Reply API เท่านั้น
    """
    if not reply_token:
        print(
            f"⚠️ ไม่สามารถส่งข้อความ Reply ได้เนื่องจากไม่มี "
            f"reply_token (ข้อความ: {text})"
        )
        return False

    if not LINE_TOKEN:
        print("❌ ไม่พบ LINE_TOKEN ในไฟล์ .env")
        return False

    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }

    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        print(
            f"Reply Response Status: {response.status_code}, "
            f"Body: {response.text}"
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ LINE Reply API: {e}")
        return False


def process_and_reply(reply_token):
    """
    รันงานเดิมเบื้องหลัง:
    ดาวน์โหลด -> กรอง -> Reply

    ไม่เปลี่ยน Logic ของ downloader / processor
    """
    global is_processing

    try:
        print("1. สั่งรันดาวน์โหลดรายงาน...")
        file_path = download_report()
        print(f"ดาวน์โหลดสำเร็จ: {file_path}")

        print("2. กรองข้อมูล...")
        data_list = process_disconnect_data(file_path)
        print(f"คัดกรองเรียบร้อย พบ {len(data_list)} รายการ")

        print("3. ส่งสรุปเข้า LINE (Reply)...")
        success = send_line_summary(
            data_list,
            reply_token=reply_token
        )

        if not success:
            print("❌ ส่งสรุปเข้า LINE ไม่สำเร็จ")

    except Exception as e:
        print(f"เกิดข้อผิดพลาดระหว่างประมวลผล: {e}")

        # พยายาม Reply แจ้ง Error โดยใช้ token เดิม
        try:
            reply_text(
                reply_token,
                f"❌ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
            )
        except Exception as ex:
            print(f"ไม่สามารถส่งข้อความแจ้ง Error ได้: {ex}")

    finally:
        with process_lock:
            is_processing = False

        print("สถานะบอท: พร้อมรับคำสั่งใหม่แล้ว")


@app.route("/webhook", methods=["POST"])
def webhook():
    global is_processing

    try:
        body = request.get_json(silent=True)
    except Exception:
        body = None

    if not body:
        return "OK", 200

    events = body.get("events", [])

    for event in events:
        if event.get("type") != "message":
            continue

        message_type = event.get("message", {}).get("type")
        text = event.get("message", {}).get("text", "").strip()

        if message_type == "text" and text in ["disconnect", "งานยกเลิก"]:
            reply_token = event.get("replyToken")

            if not reply_token:
                print("❌ LINE event ไม่มี replyToken")
                continue

            with process_lock:
                if is_processing:
                    print("ปฏิเสธคำสั่งซ้อน: บอทกำลังประมวลผลงานค้างอยู่...")

                    # คง Logic เดิมสำหรับแจ้งผู้ใช้เมื่อมีงานซ้อน
                    reply_text(
                        reply_token,
                        "⏳ บอทกำลังประมวลผลรายการก่อนหน้าอยู่ "
                        "กรุณารอสักครู่ครับ..."
                    )
                    continue

                is_processing = True

            print(
                f"ได้รับคำสั่ง: {text} "
                "กำลังเริ่มทำงานในเบื้องหลัง..."
            )

            # คงแนวทาง Background Thread เดิม
            threading.Thread(
                target=process_and_reply,
                args=(reply_token,),
                daemon=True
            ).start()

    # ต้องตอบ Webhook 200 OK ให้ LINE
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
