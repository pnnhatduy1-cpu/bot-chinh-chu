import telebot
from rembg import remove, new_session
from PIL import Image
import io
import os
import gc
import time
from flask import Flask
from threading import Thread

# --- CẤU HÌNH WEB ẢO CHO RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy ngon lành!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------

TOKEN = '8819000463:AAEPXP-1NEm6o9fBCNZTToWg2LIU42g7LoU'
BACKGROUND_PATH = 'IMG_202606271421010.JPG' 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "Đang xử lý tách nền siêu tốc và phối vào khung 'Đàn Ông Chỉnh Chu'...")
    try:
        start_time = time.time()
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_image = Image.open(io.BytesIO(downloaded_file))
        
        # Khởi tạo model siêu nhẹ u2netp chuẩn cấu hình hệ thống
        print("Đang bóc tách nền bằng AI...")
        sess = new_session("u2netp")
        subject_image = remove(input_image, session=sess) 
        
        print("Đang dán chủ thể vào phôi nền...")
        bg_image = Image.open(BACKGROUND_PATH).convert("RGBA")
        
        target_height = int(bg_image.height * 0.7)
        aspect_ratio = subject_image.width / subject_image.height
        target_width = int(target_height * aspect_ratio)
        
        if target_width > bg_image.width * 0.9:
            target_width = int(bg_image.width * 0.9)
            target_height = int(target_width / aspect_ratio)
            
        subject_resized = subject_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        position_x = (bg_image.width - subject_resized.width) // 2
        position_y = bg_image.height - subject_resized.height 
        
        bg_image.paste(subject_resized, (position_x, position_y), mask=subject_resized)
        
        final_image = bg_image.convert("RGB")
        bio = io.BytesIO()
        bio.name = 'thanh_pham.jpg'
        final_image.save(bio, 'JPEG', quality=95)
        bio.seek(0)
        
        bot.send_photo(message.chat.id, bio, caption="Lên đồ xong rồi anh Duy ơi! 🔥")
        print(f"Xử lý thành công trong {time.time() - start_time:.2s} giây!")
        
        # Giải phóng bộ nhớ
        del input_image, subject_image, bg_image, subject_resized, final_image
        gc.collect()
        
    except Exception as e:
        print(f"Lỗi rồi: {str(e)}")
        bot.reply_to(message, f"Gặp lỗi rồi anh ơi: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    print("Cổng mạng Render đã mở thành công!")
    print("Bot đang chạy...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
