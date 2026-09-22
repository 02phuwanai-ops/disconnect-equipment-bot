def format_cnfc_style(incident_no, circuit, customer_name, address, appointment_date, appointment_time, reason):
    # จัดรูปแบบข้อความให้เหมือนตัวอย่าง
    message = (
        f"🎫 : {incident_no}\n"
        f"Circuit: {circuit} {customer_name} {address}\n"
        f"นัดลูกค้า {appointment_date} เวลา {appointment_time} น. ({reason})"
    )
    return message

# ตัวอย่างข้อมูลจำลองที่ดึงมาทดสอบรันบน Local
sample_data = {
    "incident_no": "INC000103505278",
    "circuit": "J05329 23/49",
    "customer_name": "นามเปค เอ็นจิเนียริ่ง แอนด์ฯ",
    "address": "อาคารสรชัย 17 สุขุมวิท สุขุมวิท 63 คลองตันเหนือ วัฒนา",
    "appointment_date": "21/09/2026",
    "appointment_time": "10:00",
    "reason": "ลูกค้านัดเข้าตรวจสอบ"
}

if __name__ == "__main__":
    result_text = format_cnfc_style(
        sample_data["incident_no"],
        sample_data["circuit"],
        sample_data["customer_name"],
        sample_data["address"],
        sample_data["appointment_date"],
        sample_data["appointment_time"],
        sample_data["reason"]
    )
    
    print("--- ตัวอย่างข้อความที่จัดรูปแบบแล้ว ---")
    print(result_text)