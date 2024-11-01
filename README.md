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
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
AUTHORIZED_USERS=516496403


FOR RUNNING THE BOT EXECUTE COMMAND : python app.py