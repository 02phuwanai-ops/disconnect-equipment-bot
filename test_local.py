import os
import glob
import pandas as pd
import requests
from dotenv import load_dotenv

# โหลด Token จากไฟล์ .env
load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

def test_process_and_line():
    # ค้นหาไฟล์ .csv ล่าสุดในโฟลเดอร์ downloads อัตโนมัติ
    list_of_files = glob.glob('downloads/*.csv')
    if not list_of_files:
        print("❌ ไม่พบไฟล์ CSV ในโฟลเดอร์ downloads")
        return
    
    file_path = max(list_of_files, key=os.path.getctime)
    print(f"📂 กำลังอ่านไฟล์ล่าสุด: {file_path}")
    
    try:
        # อ่านไฟล์ CSV จาก True Gateway
        df = pd.read_csv(file_path, encoding='cp874', low_memory=False)
    except Exception as e:
        print(f"❌ อ่านไฟล์ไม่สำเร็จ: {e}")
        return

    print(f"📊 จำนวนข้อมูลทั้งหมดในไฟล์: {len(df)} แถว")

    # 2. กรองเฉพาะงานเก็บอุปกรณ์ (Function F) -> เช็กคอลัมน์ OIV_WORK_ACTN_CD
    if 'OIV_WORK_ACTN_CD' not in df.columns:
        print("❌ ไม่พบคอลัมน์ OIV_WORK_ACTN_CD ในไฟล์")
        return

    df_f = df[df['OIV_WORK_ACTN_CD'] == 'F'].copy()
    print(f"🔍 กรองงาน Function 'F' (เก็บอุปกรณ์) เหลือ: {len(df_f)} แถว")

    # 3. กำหนดเงื่อนไขพื้นที่
    cond_b025 = (df_f['HOP_HOZ_ORG'].str.contains('B025', na=False)) & (df_f['OIV_KHET'] == 'ห้วยขวาง')
    cond_b044 = (df_f['HOP_HOZ_ORG'].str.contains('B044', na=False)) & (df_f['OIV_KHET'].isin(['ลาดพร้าว', 'วังทองหลาง']))
    cond_b114 = (df_f['HOP_HOZ_ORG'].str.contains('B114', na=False)) & (df_f['OIV_KHET'].isin(['พระโขนง', 'คลองเตย', 'วัฒนา']))

    filtered_df = df_f[cond_b025 | cond_b044 | cond_b114]
    print(f"🎯 กรองตามเงื่อนไขพื้นที่สำเร็จ เหลือ: {len(filtered_df)} รายการ")

    # 4. จัดเตรียมข้อมูลที่จะส่ง
    results = []
    for _, row in filtered_df.iterrows():
        reason = row.get('UM_REASON') if pd.notna(row.get('UM_REASON')) else row.get('OIV_SR_DESC', '-')
        results.append({
            'order_id': row.get('OIV_ORDERID', '-'),
            'circuit': row.get('OIV_SRV_NUM', '-'),
            'customer': row.get('OIV_CUSTOMER_NAME', '-'),
            'address': row.get('OIV_CUSTOMER_ADDRESS', '-'),
            'reason': reason
        })

    # 5. ทดสอบส่งเข้า LINE
    if not LINE_TOKEN:
        print("❌ ไม่พบ LINE_TOKEN ในไฟล์ .env กรุณาตรวจสอบ")
        return

    print("🚀 กำลังส่งข้อมูลสรุปเข้า LINE...")
    
    # สร้างข้อความสรุป
    message_text = f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ (ทดสอบ Local)\nพบทั้งหมด {len(results)} รายการ\n============================== "
    
    for item in results[:5]:  # ตัวอย่างส่ง 5 รายการแรกก่อน
        message_text += f"\n\n🎫 : {item['order_id']}"
        message_text += f"\nCircuit: {item['circuit']} {item['customer']}"
        message_text += f"\n{item['reason']}"
        message_text += "\n------------------------------"

    line_to = os.getenv("LINE_TO")
    
    if not line_to:
        print("⚠️ กรุณากำหนด LINE_TO (User ID หรือ Group ID ของคุณ) ใน .env เพื่อให้ระบบส่ง Push เข้าหาคุณได้โดยตรง")
        return

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_TOKEN}'
    }
    payload = {
        'to': line_to,
        'messages': [{'type': 'text', 'text': message_text}]
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ ส่งข้อมูลเข้า LINE สำเร็จเรียบร้อยแล้ว!")
    else:
        print(f"❌ ส่ง LINE ไม่สำเร็จ Status Code: {res.status_code}, Body: {res.text}")

if __name__ == "__main__":
    test_process_and_line()