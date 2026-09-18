import os
from downloader import download_report
from processor import process_disconnect_data
from line_notifier import send_line_summary

def run():
    print("1. กำลังดาวน์โหลดไฟล์จาก Gateway True...")
    try:
        file_path = download_report()
        print(f"ดาวน์โหลดสำเร็จ: {file_path}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดาวน์โหลด: {e}")
        return

    print("2. กำลังประมวลผลข้อมูลและคัดกรองเขต...")
    data_list = process_disconnect_data(file_path)
    print(f"คัดกรองเรียบร้อย พบ {len(data_list)} รายการ")

    print("3. กำลังส่งข้อมูลเข้ากลุ่ม LINE...")
    success = send_line_summary(data_list)
    if success:
        print("ส่งข้อความเข้า LINE เรียบร้อยแล้ว!")
    else:
        print("ส่งข้อความเข้า LINE ไม่สำเร็จ")

if __name__ == "__main__":
    run()