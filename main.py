import telebot
from rembg import remove
from PIL import Image
import io

# Đã nạp Token của anh Duy vào đây
TOKEN = '8819000463:AAEPXP-1NEm6o9fBCNZTToWg2LIU42g7LoU'
BACKGROUND_PATH = 'IMG_202606271421010.JPG' 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "Đang xử lý tách nền và phối vào khung 'Đàn Ông Chỉnh Chu'...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_image = Image.open(io.BytesIO(downloaded_file))
        subject_image = remove(input_image) 
        
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
    except Exception as e:
        bot.reply_to(message, f"Gặp lỗi rồi anh ơi: {str(e)}")

print("Bot đang chạy...")
bot.polling()
