import os
import sys
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from instagrapi import Client as InstaClient
import logging
from pathlib import Path
from dotenv import load_dotenv
import contextlib

# Load environment variables
load_dotenv()

# States for conversation handler
AWAITING_MEDIA = 1

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UploadBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD')
        self.telegram_channel = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not all([self.telegram_token, self.instagram_username, 
                   self.instagram_password, self.telegram_channel]):
            logger.error("Missing environment variables")
            sys.exit(1)
        
        # Initialize Instagram client
        try:
            self.instagram = InstaClient()
            self.instagram.login(self.instagram_username, self.instagram_password)
            logger.info("Successfully connected to Instagram")
        except Exception as e:
            logger.error(f"Instagram login failed: {str(e)}")
            sys.exit(1)
        
        # Create directory for temporary files
        self.media_dir = Path('temp_media')
        self.media_dir.mkdir(exist_ok=True)
        
        # Track bot status
        self.active_users = set()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the bot and activate media handling"""
        user_id = update.effective_user.id
        self.active_users.add(user_id)
        
        keyboard = [['🚫 Stop Bot']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "✅ Bot is now active!\n\n"
            "Send me any photo or video and I'll upload it to the channel and Instagram.\n"
            "You can add a caption to your media if you want.\n\n"
            "Press '🚫 Stop Bot' when you're done.",
            reply_markup=reply_markup
        )
        
        return AWAITING_MEDIA

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stop the bot"""
        user_id = update.effective_user.id
        if user_id in self.active_users:
            self.active_users.remove(user_id)
        
        await update.message.reply_text(
            "Bot stopped. Send /start to activate it again.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END

    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle received media"""
        user_id = update.effective_user.id
        if user_id not in self.active_users:
            await update.message.reply_text(
                "Bot is not active. Send /start first!"
            )
            return AWAITING_MEDIA

        file_path = None
        status_message = None
        
        try:
            caption = update.message.caption or ""
            
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                file_path = self.media_dir / f"photo_{file_id}.jpg"
                is_video = False
            elif update.message.video:
                file_id = update.message.video.file_id
                file_path = self.media_dir / f"video_{file_id}.mp4"
                is_video = True
            else:
                await update.message.reply_text("Please send a photo or video.")
                return AWAITING_MEDIA

            status_message = await update.message.reply_text("📥 Downloading media...")

            try:
                file = await context.bot.get_file(file_id)
                await file.download_to_drive(str(file_path))

                # Upload to Telegram channel
                await status_message.edit_text("⌛ Uploading to Telegram channel...")
                
                if is_video:
                    with open(file_path, 'rb') as video_file:
                        await context.bot.send_video(
                            chat_id=self.telegram_channel,
                            video=video_file,
                            caption=caption
                        )
                else:
                    with open(file_path, 'rb') as photo_file:
                        await context.bot.send_photo(
                            chat_id=self.telegram_channel,
                            photo=photo_file,
                            caption=caption
                        )

                # Upload to Instagram
                await status_message.edit_text("⌛ Uploading to Instagram...")
                if is_video:
                    self.instagram.video_upload(str(file_path), caption=caption)
                else:
                    self.instagram.photo_upload(str(file_path), caption=caption)
                
                await status_message.edit_text("✅ Upload complete! Send another media or press '🚫 Stop Bot' when done.")

            finally:
                if file_path and os.path.exists(file_path):
                    try:
                        with contextlib.suppress(Exception):
                            import gc
                            gc.collect()
                        os.chmod(file_path, 0o777)
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Failed to delete temporary file: {str(e)}")

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            logger.error(error_msg)
            if status_message:
                await status_message.edit_text(error_msg)
            else:
                await update.message.reply_text(error_msg)

        return AWAITING_MEDIA

    async def handle_invalid_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle invalid input while bot is active"""
        if update.effective_user.id in self.active_users:
            await update.message.reply_text("Please send a photo or video, or press '🚫 Stop Bot' to stop.")
        return AWAITING_MEDIA

def main() -> None:
    # Create bot instance
    bot = UploadBot()
    
    # Create application
    application = Application.builder().token(bot.telegram_token).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            AWAITING_MEDIA: [
                MessageHandler(filters.PHOTO | filters.VIDEO, bot.handle_media),
                MessageHandler(filters.Regex('^🚫 Stop Bot$'), bot.stop),
                MessageHandler(filters.ALL & ~filters.COMMAND, bot.handle_invalid_input)
            ]
        },
        fallbacks=[CommandHandler('start', bot.start)]
    )
    
    # Add handler
    application.add_handler(conv_handler)
    
    # Run the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()