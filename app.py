import logging
import requests
import httpx
import re
from bs4 import BeautifulSoup
import telebot
import os

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

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

# Function to extract MPD links from a webpage using BeautifulSoup
def extract_mpd_links(url):
    mpd_links = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the HTML
        for link in soup.find_all('a', href=True):
            if link['href'].endswith('.mpd'):
                mpd_links.append(link['href'])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
    except Exception as e:
        logger.error(f"Error parsing HTML for {url}: {e}")

    return mpd_links

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
        # Extract the actual MPD links from the response
        mpd_links_list = mpd_links.split("MPD links found:")[1].strip().strip('[]').replace("'", "").split(",")
        response_message = "Found the following .mpd links:\n" + "\n".join([link.strip() for link in mpd_links_list])
    else:
        response_message = mpd_links  # If there was an error or no links found, use the message from get_mpd_link

    bot.reply_to(message, response_message)

# Start polling to listen for incoming messages
bot.infinity_polling()