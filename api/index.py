import requests, hashlib, base64, os, random, string
from flask import Flask, request

app = Flask(__name__)

# Cấu hình lấy từ Vercel Dashboard
GITHUB_TOKEN = os.environ.get("GH_TOKEN") 
REPO = "nguyentuankhanh01022012-cloud/KeySystem"

def generate_key():
    return "FREE-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

@app.route('/verify')
def verify():
    hwid = request.args.get('hwid')
    secret = request.args.get('s') # Mã bí mật chống spam

    if not hwid or secret != "OxyDRA2026":
        return "<h1>❌ Truy cập bị từ chối!</h1>", 403

    # Tạo tên file bí mật bằng MD5 của HWID
    file_name = hashlib.md5(hwid.encode()).hexdigest() + ".txt"
    path = f"db/{file_name}"
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Nội dung ghi vào file (Key mới)
    new_key = generate_key()
    encoded_content = base64.b64encode(new_key.encode()).decode()

    # Kiểm tra xem máy này đã từng có key chưa để lấy SHA (tránh lỗi 422)
    get_res = requests.get(url, headers=headers).json()
    sha = get_res.get('sha')

    payload = {
        "message": f"Kích hoạt HWID: {hwid}",
        "content": encoded_content
    }
    if sha: payload["sha"] = sha

    # Ghi file lên GitHub
    res = requests.put(url, headers=headers, json=payload)
    
    if res.status_code in [200, 201]:
        return f"""
        <div style="text-align:center; padding:50px; font-family:sans-serif;">
            <h1 style="color:green;">✅ KÍCH HOẠT THÀNH CÔNG!</h1>
            <p>Mã máy: <b>{hwid}</b></p>
            <p>Key của bạn: <b style="color:blue;">{new_key}</b></p>
            <hr>
            <p><b>Vui lòng chờ 30 giây để hệ thống đồng bộ rồi mới mở Tool.</b></p>
        </div>
        """
    return "<h1>❌ Lỗi kết nối GitHub!</h1>", 500
