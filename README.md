your_project_folder/
├── app.py
├── .env
└── temp_media/     # Will be created automatically



# Core dependencies
pip install python-telegram-bot  # For Telegram bot functionality
pip install instagrapi          # For Instagram API
pip install python-dotenv       # For environment variables
pip install httpx              # Required by python-telegram-bot


# Create .env file with these variables:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
TELEGRAM_CHANNEL_ID=@your_channel_name



FOR RUNNING THE BOT EXECUTE COMMAND : app.py