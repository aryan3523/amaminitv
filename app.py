import os
import logging
import requests
import httpx
import re
from bs4 import BeautifulSoup
import telebot
from fastapi import FastAPI
from threading import Thread
import uvicorn

# Initialize the bot with the token from environment variable
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get MPD links using httpx (same as before)
def get_mpd_link(url):
    try:
        response = httpx.get(url, headers=headers)
        if response.status_code != 200:
            return f"Failed to retrieve the page: Status code {response.status_code}"
        page_content = response.text
        mpd_pattern = r'(https?://[^\s]+\.mpd)'
        mpd_links = re.findall(mpd_pattern, page_content)

        if mpd_links:
            mpd_links = list(set(mpd_links))  # Remove duplicates
            return f"MPD links found: {mpd_links}"
        else:
            return "No .mpd link found on the page."

    except Exception as e:
        return f"Error occurred: {str(e)}"

# Command handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me a URL and I will find .mpd links for you.")

# Message handler for processing URLs and returning MPD links
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text  # Get the URL from the user's message
    mpd_links = get_mpd_link(url)  # Pass the URL to the get_mpd_link function

    if mpd_links.startswith("MPD links found:"):
        mpd_links_list = mpd_links.split("MPD links found:")[1].strip().strip('[]').replace("'", "").split(",")
        response_message = "Found the following .mpd links:\n" + "\n".join([link.strip() for link in mpd_links_list])
    else:
        response_message = mpd_links  # If there was an error or no links found, use the message from get_mpd_link

    bot.reply_to(message, response_message)

# Function to start the bot
def start_bot():
    logging.info("Starting the bot...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Error occurred while polling: {e}")

# Create a FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Telegram bot is running!"}

if __name__ == "__main__":
    # Run the bot in a separate thread
    Thread(target=start_bot).start()

    # Start FastAPI web server on the dynamically assigned port
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
