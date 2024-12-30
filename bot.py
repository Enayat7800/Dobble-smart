import telebot
import os

# Load bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Global Variables
source_channel_ids = []
destination_channel_id = None
copying_enabled = False


# Helper function to check if source and destination channel IDs are set
def check_channel_ids(message):
    global source_channel_ids, destination_channel_id
    if not source_channel_ids or not destination_channel_id:
        bot.reply_to(message, "Please set the source and destination channel IDs first.")
        return False
    return True


# Command handler for /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = """
Namaste! This bot helps you copy messages from other Telegram channels and post them to your channel.

**Available Commands:**

/help - Information about the bot and contact details.
/setsource <channel_id1> <channel_id2> ... - Set the IDs of channels from which to copy messages.
/setdestination <channel_id> - Set the ID of the channel where to post messages.
/startcopy - Start copying messages.
/stopcopy - Stop copying messages.
/removesource - Remove source channel IDs.
/removedestination - Remove destination channel ID.
/status - View the current status of the bot.

To get started, please set the source and destination channel IDs.
"""
    bot.reply_to(message, welcome_message)


# Command handler for /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
This bot helps you copy messages from other Telegram channels and post them to your channel.

**Available Commands:**

/setsource <channel_id1> <channel_id2> ... - Set the IDs of channels from which to copy messages.
/setdestination <channel_id> - Set the ID of the channel where to post messages.
/startcopy - Start copying messages.
/stopcopy - Stop copying messages.
/removesource - Remove source channel IDs.
/removedestination - Remove destination channel ID.
/status - View the current status of the bot.

For any assistance, contact: @captain_stive
"""
    bot.reply_to(message, help_message)


# Command handler for /setsource
@bot.message_handler(commands=['setsource'])
def set_source(message):
    global source_channel_ids
    try:
        ids = message.text.split()[1:]
        source_channel_ids = [int(id) for id in ids]
        bot.reply_to(message, f"Source channel IDs set: {source_channel_ids}")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /setsource <channel_id1> <channel_id2> ...")


# Command handler for /setdestination
@bot.message_handler(commands=['setdestination'])
def set_destination(message):
    global destination_channel_id
    try:
        destination_channel_id = int(message.text.split()[1])
        bot.reply_to(message, f"Destination channel ID set: {destination_channel_id}")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /setdestination <channel_id>")


# Command handler for /startcopy
@bot.message_handler(commands=['startcopy'])
def start_copying(message):
    global copying_enabled
    if check_channel_ids(message):
        copying_enabled = True
        bot.reply_to(message, "Started copying messages.")


# Command handler for /stopcopy
@bot.message_handler(commands=['stopcopy'])
def stop_copying(message):
    global copying_enabled
    copying_enabled = False
    bot.reply_to(message, "Stopped copying messages.")


# Command handler for /removesource
@bot.message_handler(commands=['removesource'])
def remove_source(message):
    global source_channel_ids
    source_channel_ids = []
    bot.reply_to(message, "Source channel IDs removed.")


# Command handler for /removedestination
@bot.message_handler(commands=['removedestination'])
def remove_destination(message):
    global destination_channel_id
    destination_channel_id = None
    bot.reply_to(message, "Destination channel ID removed.")


# Command handler for /status
@bot.message_handler(commands=['status'])
def show_status(message):
    status_message = f"""
**Current Bot Status:**

Copying enabled: {copying_enabled}
Source channel IDs: {source_channel_ids if source_channel_ids else 'None'}
Destination channel ID: {destination_channel_id if destination_channel_id else 'None'}
"""
    bot.reply_to(message, status_message)

# Message handler to copy messages
@bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'document', 'sticker', 'voice', 'video_note'])
def handle_messages(message):
    global copying_enabled, source_channel_ids, destination_channel_id
    
    if copying_enabled and message.chat.type == 'channel' and message.sender_chat:
      if message.sender_chat.id in source_channel_ids:
            try:
                # Copy message based on its type
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


# Run the bot
print("Bot is running...")
bot.polling(none_stop=True)
