import pandas as pd

def process_disconnect_data(file_path):
    try:
        # อ่านไฟล์จาก True Gateway (ใช้ Comma เป็นตัวคั่น และ Encoding ภาษาไทย)
        df = pd.read_csv(file_path, encoding='cp874', low_memory=False)
    except Exception as e:
        print(f"❌ อ่านไฟล์ไม่สำเร็จ: {e}")
        return []

    # 1. กรองเฉพาะงานเก็บอุปกรณ์ (Function F) -> เช็กคอลัมน์ OIV_WORK_ACTN_CD
    if 'OIV_WORK_ACTN_CD' not in df.columns:
        print("❌ ไม่พบคอลัมน์ OIV_WORK_ACTN_CD ในไฟล์")
        return []

    df_f = df[df['OIV_WORK_ACTN_CD'] == 'F'].copy()

    # 2. กำหนดเงื่อนไขพื้นที่ (ตามที่คุณตั้งค่าไว้)
    cond_b025 = (df_f['HOP_HOZ_ORG'].str.contains('B025', na=False)) & (df_f['OIV_KHET'] == 'ห้วยขวาง')
    cond_b044 = (df_f['HOP_HOZ_ORG'].str.contains('B044', na=False)) & (df_f['OIV_KHET'].isin(['ลาดพร้าว', 'วังทองหลาง']))
    cond_b114 = (df_f['HOP_HOZ_ORG'].str.contains('B114', na=False)) & (df_f['OIV_KHET'].isin(['พระโขนง', 'คลองเตย', 'วัฒนา']))

    filtered_df = df_f[cond_b025 | cond_b044 | cond_b114]
    
    results = []
    for _, row in filtered_df.iterrows():
        # ดึงฟิลด์ข้อมูลสำคัญตามที่คุณระบุ
        reason = row.get('UM_REASON') if pd.notna(row.get('UM_REASON')) else row.get('OIV_SR_DESC', '-')
        
        results.append({
            'order_id': row.get('OIV_ORDERID', '-'),
            'circuit': row.get('OIV_SRV_NUM', '-'), # ใช้ OIV_SRV_NUM ตามหัวข้อจริงในไฟล์
            'customer': row.get('OIV_CUSTOMER_NAME', '-'),
            'address': row.get('OIV_CUSTOMER_ADDRESS', '-'),
            'phone': row.get('OIV_CONTACTNUMBER', '-'),
            'building': row.get('SI_BUILDING', '-'),
            'khet': row.get('OIV_KHET', '-'),
            'khwang': row.get('OIV_KHWANG', '-'),
            'reason': reason
        })
        
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        data = process_disconnect_data(sys.argv[1])
        print(f"พบข้อมูลที่ตรงเงื่อนไข: {len(data)} รายการ")