import telebot

# **जरूरी:** नीचे दी गई जानकारी को अपनी जानकारी से बदलें।
BOT_TOKEN = "YOUR_BOT_TOKEN"  # अपने बॉट टोकन को यहाँ डालें (बॉटफादर से प्राप्त करें)

bot = telebot.TeleBot(BOT_TOKEN)

# चर जहाँ चैनल ID संग्रहीत किए जाएंगे
source_channel_id = None
destination_channel_id = None
copying_enabled = False

# हेल्पर फंक्शन यह जांचने के लिए कि क्या चैनल आईडी सेट हैं
def check_channel_ids(message):
    global source_channel_id, destination_channel_id
    if not source_channel_id or not destination_channel_id:
        bot.reply_to(message, "कृपया पहले स्रोत और गंतव्य चैनल आईडी सेट करें।")
        return False
    return True

# स्टार्ट कमांड हैंडलर
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = """
नमस्ते! यह बॉट दूसरे टेलीग्राम चैनलों से संदेश कॉपी करके आपके चैनल में पोस्ट करने में आपकी मदद करता है।

**उपलब्ध कमांड:**

/setsource <चैनल_आईडी> - उस चैनल का आईडी सेट करें जिससे संदेश कॉपी करने हैं।
/setdestination <चैनल_आईडी> - उस चैनल का आईडी सेट करें जहाँ संदेश पोस्ट करने हैं।
/startcopy - संदेशों की कॉपी करना शुरू करें।
/stopcopy - संदेशों की कॉपी करना बंद करें।

शुरू करने के लिए, कृपया स्रोत और गंतव्य चैनल आईडी सेट करें।
"""
    bot.reply_to(message, welcome_message)

# कमांड हैंडलर: स्रोत चैनल सेट करें
@bot.message_handler(commands=['setsource'])
def set_source(message):
    global source_channel_id
    try:
        source_channel_id = int(message.text.split()[1])
        bot.reply_to(message, f"स्रोत चैनल आईडी सेट किया गया: {source_channel_id}")
    except (IndexError, ValueError):
        bot.reply_to(message, "उपयोग: /setsource <चैनल_आईडी>")

# कमांड हैंडलर: गंतव्य चैनल सेट करें
@bot.message_handler(commands=['setdestination'])
def set_destination(message):
    global destination_channel_id
    try:
        destination_channel_id = int(message.text.split()[1])
        bot.reply_to(message, f"गंतव्य चैनल आईडी सेट किया गया: {destination_channel_id}")
    except (IndexError, ValueError):
        bot.reply_to(message, "उपयोग: /setdestination <चैनल_आईडी>")

# कमांड हैंडलर: कॉपी करना शुरू करें
@bot.message_handler(commands=['startcopy'])
def start_copying(message):
    global copying_enabled
    if check_channel_ids(message):
        copying_enabled = True
        bot.reply_to(message, "संदेशों की कॉपी करना शुरू किया गया।")

# कमांड हैंडलर: कॉपी करना बंद करें
@bot.message_handler(commands=['stopcopy'])
def stop_copying(message):
    global copying_enabled
    copying_enabled = False
    bot.reply_to(message, "संदेशों की कॉपी करना बंद किया गया।")

# मैसेज हैंडलर: संदेशों को कॉपी करें
@bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'document', 'sticker', 'voice', 'video_note'])
def handle_messages(message):
    global copying_enabled, source_channel_id, destination_channel_id
    if copying_enabled and message.chat.type == 'channel' and message.sender_chat and message.sender_chat.id == source_channel_id:
        try:
            # संदेश के प्रकार के आधार पर उसे कॉपी करके अपने चैनल में पोस्ट करें
            if message.text:
                bot.send_message(chat_id=destination_channel_id, text=message.text)
            elif message.photo:
                photo = message.photo[-1].file_id
                caption = message.caption
                bot.send_photo(chat_id=destination_channel_id, photo=photo, caption=caption)
            elif message.video:
                video = message.video.file_id
                caption = message.caption
                bot.send_video(chat_id=destination_channel_id, video=video, caption=caption)
            elif message.audio:
                audio = message.audio.file_id
                caption = message.caption
                performer = message.audio.performer
                title = message.audio.title
                caption_text = f"**{performer or ''} - {title or ''}**\n\n{caption or ''}" if performer or title or caption else None
                bot.send_audio(chat_id=destination_channel_id, audio=audio, caption=caption_text)
            elif message.document:
                document = message.document.file_id
                caption = message.caption
                file_name = message.document.file_name
                caption_text = f"**{file_name}**\n\n{caption or ''}" if file_name or caption else None
                bot.send_document(chat_id=destination_channel_id, document=document, caption=caption_text)
            elif message.sticker:
                sticker = message.sticker.file_id
                bot.send_sticker(chat_id=destination_channel_id, sticker=sticker)
            elif message.voice:
                voice = message.voice.file_id
                caption = message.caption
                bot.send_voice(chat_id=destination_channel_id, voice=voice, caption=caption)
            elif message.video_note:
                video_note = message.video_note.file_id
                bot.send_video_note(chat_id=destination_channel_id, video_note=video_note)

            print(f"Message from channel {message.chat.title} copied and posted successfully.")
        except Exception as e:
            print(f"Error copying and posting message: {e}")

print("बॉट चल रहा है...")
bot.polling(none_stop=True)
