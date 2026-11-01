import os
import glob
from flask import Flask, render_template_string, jsonify, send_from_directory
from downloader import download_report
from processor import process_disconnect_data

app = Flask(__name__)

# กำหนดโฟลเดอร์สำหรับดาวน์โหลดไฟล์
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Disconnect Equipment Bot - Dashboard Pro</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --success: #10b981;
            --success-hover: #059669;
            --danger: #ef4444;
            --danger-hover: #dc2626;
            --border: #334155;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            margin: 0;
            padding: 20px;
            color: var(--text-color);
        }
        .container {
            max-width: 850px;
            margin: 30px auto;
            background: var(--card-bg);
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            border: 1px solid var(--border);
        }
        h2 {
            color: #f1f5f9;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        p {
            color: var(--text-muted);
        }
        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        button {
            border: none;
            padding: 12px 20px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary { background-color: var(--success); color: white; }
        .btn-primary:hover { background-color: var(--success-hover); }
        .btn-secondary { background-color: var(--primary); color: white; }
        .btn-secondary:hover { background-color: var(--primary-hover); }
        .btn-danger { background-color: #64748b; color: white; }
        .btn-danger:hover { background-color: #475569; }
        button:disabled { background-color: #475569; opacity: 0.6; cursor: not-allowed; }
        
        .loading {
            display: none;
            color: #f59e0b;
            font-weight: 600;
            margin-top: 15px;
        }
        .status-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            font-weight: 600;
            display: none;
            border: 1px solid transparent;
        }
        .status-success { background-color: rgba(16, 185, 129, 0.1); color: #34d399; border-color: rgba(16, 185, 129, 0.2); }
        .status-error { background-color: rgba(239, 68, 68, 0.1); color: #f87171; border-color: rgba(239, 68, 68, 0.2); }

        .textarea-container {
            position: relative;
            margin-top: 25px;
        }
        label {
            font-weight: 600;
            color: #e2e8f0;
            display: block;
            margin-bottom: 8px;
        }
        textarea {
            width: 100%;
            height: 320px;
            padding: 15px;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
            border: 1px solid var(--border);
            border-radius: 8px;
            box-sizing: border-box;
            background: #0f172a;
            color: #f87171;
            resize: vertical;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛠️ Disconnect Equipment Bot <span style="font-size: 14px; background: #334155; padding: 4px 10px; border-radius: 20px; color: #38bdf8;">Dashboard Pro</span></h2>
        <p>ระบบดึงรายงานอัตโนมัติ กรองเฉพาะงานเก็บอุปกรณ์ (Disconnect) และเตรียมข้อความสำหรับนำไปวางใน LINE</p>
        
        <div class="btn-group">
            <button id="runBtn" class="btn-primary" onclick="runBot()">🚀 สั่งดาวน์โหลดและประมวลผล</button>
            <button id="clearBtn" class="btn-danger" onclick="clearText()">🧹 ล้างข้อความ</button>
            <a id="downloadCsvBtn" style="display:none;" class="btn-secondary" href="#" target="_blank">📥 ดาวน์โหลดไฟล์ CSV ดิบ</a>
        </div>
        
        <div id="loading" class="loading">⏳ กำลังเปิดเบราว์เซอร์ดาวน์โหลดรายงานจาก True Gateway และคัดกรองข้อมูล... กรุณารอสักครู่ (10-30 วินาที)</div>
        <div id="statusBox" class="status-box"></div>

        <div class="textarea-container">
            <label for="resultText">📋 ข้อความสรุปสำหรับนำไปวางใน LINE:</label>
            <textarea id="resultText" placeholder="ผลลัพธ์จะแสดงที่นี่หลังจากประมวลผลเสร็จ..."></textarea>
        </div>
        
        <div class="btn-group" style="margin-top: 15px;">
            <button class="btn-secondary" onclick="copyText()">📋 คัดลอกข้อความทั้งหมด</button>
        </div>
    </div>

    <script>
        async function runBot() {
            const btn = document.getElementById('runBtn');
            const loading = document.getElementById('loading');
            const statusBox = document.getElementById('statusBox');
            const resultText = document.getElementById('resultText');
            const downloadCsvBtn = document.getElementById('downloadCsvBtn');

            btn.disabled = true;
            loading.style.display = 'block';
            statusBox.style.display = 'none';
            resultText.value = '';
            downloadCsvBtn.style.display = 'none';

            try {
                let response = await fetch('/run-process', { method: 'POST' });
                let data = await response.json();

                if (data.status === 'success') {
                    resultText.value = data.message;
                    statusBox.className = 'status-box status-success';
                    statusBox.innerText = `✅ สำเร็จ! ดึงข้อมูลและคัดกรองเรียบร้อย พบทั้งหมด ${data.count} รายการ`;
                    statusBox.style.display = 'block';
                    
                    if (data.filename) {
                        downloadCsvBtn.href = `/download-csv/${data.filename}`;
                        downloadCsvBtn.style.display = 'inline-flex';
                    }
                } else {
                    statusBox.className = 'status-box status-error';
                    statusBox.innerText = `❌ เกิดข้อผิดพลาด: ${data.message}`;
                    statusBox.style.display = 'block';
                }
            } catch (err) {
                statusBox.className = 'status-box status-error';
                statusBox.innerText = `❌ เชื่อมต่อ Server ไม่สำเร็จ: ${err}`;
                statusBox.style.display = 'block';
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }

        function copyText() {
            const textZone = document.getElementById('resultText');
            if (!textZone.value.trim()) {
                alert('⚠️ ไม่มีข้อความให้คัดกรอง!');
                return;
            }
            textZone.select();
            document.execCommand('copy');
            alert('📋 คัดลอกข้อความเรียบร้อยแล้ว! สามารถนำไปวางใน LINE ได้เลยครับ');
        }

        function clearText() {
            document.getElementById('resultText.value') = '';
            document.getElementById('resultText').value = '';
            document.getElementById('statusBox').style.display = 'none';
            document.getElementById('downloadCsvBtn').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/run-process", methods=["POST"])
def run_process():
    file_path = None
    try:
        # 1. สั่งดาวน์โหลดไฟล์จาก True Gateway
        file_path = download_report()
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "ไม่พบไฟล์ที่ดาวน์โหลดจาก True Gateway"})

        filename = os.path.basename(file_path)

        # 2. ประมวลผลและคัดกรองข้อมูลผ่าน processor.py
        data_list = process_disconnect_data(file_path)

        # 3. จัดรูปแบบข้อความ (ใช้ไอคอน 🔌 ตามที่คุณต้องการ)
        if not data_list:
            message_text = (
                "📋 สรุปงาน Disconnect เก็บอุปกรณ์ (+7 วันอนาคต)\n"
                "❌ ไม่พบรายการในเขตที่กำหนด"
            )
        else:
            message_parts = [
                f"📋 สรุปงาน Disconnect เก็บอุปกรณ์ ({len(data_list)} รายการ)",
                "=============================="
            ]

            for item in data_list:
                message_parts.append(
                    f"\n🔌 : {item['order_id']}"
                    f"\nCircuit: {item['circuit']}"
                    f"\nลูกค้า: {item['customer']}"
                    f"\nสถานที่: {item['address']}"
                    f"\nโทร: {item['phone']}"
                    f"\n{item['reason']}"
                    f"\n------------------------------"
                )

            message_text = "\n".join(message_parts)

        return jsonify({
            "status": "success",
            "count": len(data_list),
            "message": message_text,
            "filename": filename
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/download-csv/<filename>")
def download_csv(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)