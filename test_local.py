import os
import glob
import pandas as pd
from dotenv import load_dotenv

# ============================================================
# LOCAL TEST / PREVIEW ONLY
# - คง Logic การอ่าน CSV และการกรองพื้นที่เดิม
# - ไม่มีการยิง LINE API
# - ไม่มี Push
# - ใช้ตรวจสอบข้อความก่อนใช้งานจริงผ่าน LINE Webhook
# ============================================================

load_dotenv()


def test_process_and_line():
    # 1. ค้นหาไฟล์ .csv ล่าสุดในโฟลเดอร์ downloads อัตโนมัติ
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

    # 2. กรองเฉพาะงานเก็บอุปกรณ์ (Function F)
    if 'OIV_WORK_ACTN_CD' not in df.columns:
        print("❌ ไม่พบคอลัมน์ OIV_WORK_ACTN_CD ในไฟล์")
        return

    df_f = df[df['OIV_WORK_ACTN_CD'] == 'F'].copy()
    print(f"🔍 กรองงาน Function 'F' (เก็บอุปกรณ์) เหลือ: {len(df_f)} แถว")

    # 3. กำหนดเงื่อนไขพื้นที่ - คง Logic เดิม
    cond_b025 = (
        (df_f['HOP_HOZ_ORG'].str.contains('B025', na=False))
        & (df_f['OIV_KHET'] == 'ห้วยขวาง')
    )
    cond_b044 = (
        (df_f['HOP_HOZ_ORG'].str.contains('B044', na=False))
        & (df_f['OIV_KHET'].isin(['ลาดพร้าว', 'วังทองหลาง']))
    )
    cond_b114 = (
        (df_f['HOP_HOZ_ORG'].str.contains('B114', na=False))
        & (df_f['OIV_KHET'].isin(['พระโขนง', 'คลองเตย', 'วัฒนา']))
    )

    filtered_df = df_f[cond_b025 | cond_b044 | cond_b114]
    print(f"🎯 กรองตามเงื่อนไขพื้นที่สำเร็จ เหลือ: {len(filtered_df)} รายการ")

    # 4. จัดเตรียมข้อมูล - คง Logic เดิม และเพิ่ม phone ให้ตรงกับ processor.py
    results = []
    for _, row in filtered_df.iterrows():
        reason = (
            row.get('UM_REASON')
            if pd.notna(row.get('UM_REASON'))
            else row.get('OIV_SR_DESC', '-')
        )

        results.append({
            'order_id': row.get('OIV_ORDERID', '-'),
            'circuit': row.get('OIV_SRV_NUM', '-'),
            'customer': row.get('OIV_CUSTOMER_NAME', '-'),
            'address': row.get('OIV_CUSTOMER_ADDRESS', '-'),
            'phone': row.get('OIV_CONTACTNUMBER', '-'),
            'building': row.get('SI_BUILDING', '-'),
            'khet': row.get('OIV_KHET', '-'),
            'khwang': row.get('OIV_KHWANG', '-'),
            'reason': reason
        })

    # 5. Local Preview เท่านั้น
    # ห้ามยิง Push / Reply เพราะ Local ไม่มี reply_token
    print("\n" + "=" * 60)
    print("📱 LOCAL PREVIEW — ไม่มีการส่งข้อความเข้า LINE")
    print("=" * 60)

    if not results:
        message_text = (
            "📋 สรุปงาน Disconnect เก็บอุปกรณ์ (+7 วันอนาคต)\n"
            "❌ ไม่พบรายการในเขตที่กำหนด"
        )
    else:
        message_parts = [
            f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ ({len(results)} รายการ)",
            "=============================="
        ]

        for item in results[:5]:
            message_parts.append(
                f"\n🎫 : {item['order_id']}"
                f"\nCircuit: {item['circuit']}"
                f"\nลูกค้า: {item['customer']}"
                f"\nสถานที่: {item['address']}"
                f"\nโทร: {item['phone']}"
                f"\n{item['reason']}"
                f"\n------------------------------"
            )

        message_text = "\n".join(message_parts)

    print(message_text)
    print("=" * 60)
    print("ℹ️ Local Test จบแล้ว — ไม่มี LINE API ถูกเรียกใช้")
    print("ℹ️ การส่งจริงให้พิมพ์คำสั่งผ่าน LINE Webhook เท่านั้น")
    print("=" * 60)


if __name__ == "__main__":
    test_process_and_line()
