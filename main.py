import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread

# --- CẤU HÌNH WEB ẢO CHO RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot làm nét ảnh AI đang chạy mượt mà!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------

TOKEN = '8819000463:AAEPXP-1NEm6o9fBCNZTToWg2LIU42g7LoU'

# ĐÃ TÍCH HỢP MÃ REPLICATE TOKEN CỦA ANH DUY
REPLICATE_API_TOKEN = 'r8_QDIutZSQhwzFHA7h6CK66CKeGsyevVP2ZePvE'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "⚡ Bot đã nhận ảnh! Đang gửi lên hệ thống AI xử lý làm nét và phục hồi chi tiết...")
    try:
        # 1. Lấy link ảnh từ Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # 2. Cấu hình gửi lệnh sang AI Replicate (Dùng model Real-ESRGAN chuyên phục hồi ảnh vỡ)
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "version": "da23564483510ec89907ee800e4758b10dc9b28bda34241ac363198de7e93737",
            "input": {
                "image": file_url,
                "scale": 2,          # Phóng to và làm nét gấp đôi độ phân giải gốc
                "face_enhance": True # Tự động tối ưu, làm nét và làm mịn chi tiết da mặt
            }
        }
        
        response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
        prediction = response.json()
        
        if response.status_code != 201:
            bot.send_message(message.chat.id, "❌ Gặp lỗi kết nối với hệ thống AI làm nét. Anh kiểm tra lại tài khoản Replicate nhé.")
            return
            
        prediction_id = prediction["id"]
        status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        
        # 3. Vòng lặp chờ AI xử lý (Thường chỉ mất từ 3 - 6 giây)
        start_time = time.time()
        while True:
            # Kiểm tra xem tài khoản mới tạo có bị bắt đợi lâu không
            if time.time() - start_time > 60: 
                bot.send_message(message.chat.id, "⏱️ Hệ thống AI đang bận xếp hàng xử lý, anh đợi thêm một chút nhé...")
                start_time = time.time() # reset thời gian thông báo
                
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            
            if status_data["status"] == "succeeded":
                output_url = status_data["output"]
                # Trả ảnh siêu nét về phòng chat Telegram cho anh Duy
                bot.send_photo(message.chat.id, output_url, caption="Ảnh của anh đã được AI phục hồi làm nét căng! 🔥 Super Clean!")
                print("Làm nét ảnh thành công hoàn toàn!")
                break
            elif status_data["status"] == "failed":
                bot.send_message(message.chat.id, "❌ AI xử lý làm nét tấm ảnh này bị thất bại. Anh thử tấm khác xem sao.")
                break
                
            time.sleep(2) # Cứ 2 giây kiểm tra trạng thái 1 lần
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Gặp lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    print("Bot làm nét ảnh AI đang sẵn sàng lắng nghe...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
