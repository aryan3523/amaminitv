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
from mcc import get_title_from_url, get_m3u8_link

# Initialize the bot with the token from environment variable
bot = telebot.TeleBot('7527363398:AAFWaUZ913Nbdequ4OQ6oJRwJMH9FyTJs5U')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define headers globally
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Function to get title from URL
def get_title_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.strip()
        return title
    except Exception as e:
        print(f"Error fetching title for {url}: {e}")
        return "Could not fetch title"

# Function to get MPD links using httpx
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
    url = message.text
    title_name = get_title_from_url(url)
    mpd_links = get_mpd_link(url)
    m3u8_link = get_m3u8_link(url)
    
    if mpd_links.startswith("MPD links found:"):
        mpd_links_list = mpd_links.split("MPD links found:")[1].strip().strip('[]').replace("'", "").split(",")
        response_message = f"Title: {title_name}\n\nFound the following .mpd links:\n" + "\n".join([link.strip() for link in mpd_links_list])
    else:
        response_message = mpd_links
    
    if m3u8_link:
        response_message += f"\n\nFound .m3u8 link: {m3u8_link}"
    
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
