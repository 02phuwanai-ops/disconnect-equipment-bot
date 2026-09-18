import pandas as pd

def process_disconnect_data(file_path):
    # รองรับการอ่านไฟล์ CSV
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception:
        df = pd.read_csv(file_path, encoding='cp874')

    # 1. กรองเฉพาะงานเก็บอุปกรณ์ (Function F)
    df_f = df[df['OIV_WORK_ACTN_CD'] == 'F'].copy()

    # 2. กำหนดเงื่อนไขพื้นที่
    cond_b025 = (df_f['HOP_HOZ_ORG'].str.contains('B025', na=False)) & (df_f['OIV_KHET'] == 'ห้วยขวาง')
    cond_b044 = (df_f['HOP_HOZ_ORG'].str.contains('B044', na=False)) & (df_f['OIV_KHET'].isin(['ลาดพร้าว', 'วังทองหลาง']))
    cond_b114 = (df_f['HOP_HOZ_ORG'].str.contains('B114', na=False)) & (df_f['OIV_KHET'].isin(['พระโขนง', 'คลองเตย', 'วัฒนา']))

    filtered_df = df_f[cond_b025 | cond_b044 | cond_b114]
    
    results = []
    for _, row in filtered_df.iterrows():
        reason = row.get('UM_REASON') if pd.notna(row.get('UM_REASON')) else row.get('OIV_SR_DESC', '-')
        results.append({
            'khet': row.get('OIV_KHET', '-'),
            'customer': row.get('OIV_CUSTOMER_NAME', '-'),
            'address': row.get('OIV_CUSTOMER_ADDRESS', '-'),
            'phone': row.get('OIV_CONTACTNUMBER', '-'),
            'reason': reason
        })
        
    return results

if __name__ == "__main__":
    # ทดสอบฟังก์ชัน
    import sys
    if len(sys.argv) > 1:
        data = process_disconnect_data(sys.argv[1])
        print(f"พบ {len(data)} รายการ")