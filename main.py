import telebot
import requests
from PIL import Image
import io
import os
from flask import Flask
from threading import Thread

# --- CẤU HÌNH WEB ẢO CHO RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot hoạt động mượt mà không tốn RAM!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------

TOKEN = '8819000463:AAEPXP-1NEm6o9fBCNZTToWg2LIU42g7LoU'
BACKGROUND_PATH = 'IMG_202606271421010.JPG' 
REMOVE_BG_API_KEY = 'HVG9v7WgM7hv2RCzkzSabmww'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "Đang xử lý tách nền siêu tốc và căn chỉnh khung hình chuẩn 'Đàn Ông Chỉnh Chu'...")
    try:
        # 1. Tải ảnh từ Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        # 2. Gọi API ngoài tách nền hộ
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            data={'image_url': file_url, 'size': 'auto'},
            headers={'X-API-Key': REMOVE_BG_API_KEY},
        )
        
        if response.status_code == 200:
            subject_image = Image.open(io.BytesIO(response.content))
        else:
            bot.send_message(message.chat.id, "Lỗi hệ thống tách nền, anh kiểm tra tài khoản Remove.bg nhé!")
            return

        # 3. Tiến hành ghép phôi nền với tỷ lệ MỚI phóng to chủ thể
        bg_image = Image.open(BACKGROUND_PATH).convert("RGBA")
        
        # ĐỔI CHIẾN THUẬT: Ép theo chiều rộng (Người mẫu chiếm 90% bề ngang khung hình để nhìn to, rõ nét)
        target_width = int(bg_image.width * 0.9)
        aspect_ratio = subject_image.width / subject_image.height
        target_height = int(target_width / aspect_ratio)
        
        # Khống chế nếu chiều cao sau khi phóng to vượt quá 75% khung hình thì thu lại tí để tránh đè chữ
        if target_height > bg_image.height * 0.75:
            target_height = int(bg_image.height * 0.75)
            target_width = int(target_height * aspect_ratio)
            
        subject_resized = subject_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Căn giữa theo chiều ngang
        position_x = (bg_image.width - subject_resized.width) // 2
        
        # Đẩy vị trí đứng: Cách đáy một khoảng nhỏ (khoảng 3% chiều cao) giúp bố cục thoáng và sang hơn
        position_y = bg_image.height - subject_resized.height - int(bg_image.height * 0.03)
        
        bg_image.paste(subject_resized, (position_x, position_y), mask=subject_resized)
        
        final_image = bg_image.convert("RGB")
        bio = io.BytesIO()
        bio.name = 'thanh_pham.jpg'
        final_image.save(bio, 'JPEG', quality=95)
        bio.seek(0)
        
        # Gửi ảnh thành phẩm thẳng vào phòng chat
        bot.send_photo(message.chat.id, bio, caption="Lên đồ xong rồi anh Duy ơi! 🔥 Chuẩn đẹp trai chỉnh chu nhé!")
        print("Xử lý thành công hoàn toàn!")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Gặp lỗi rồi anh ơi: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    print("Bot đang sẵn sàng lắng nghe...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
