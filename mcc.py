import httpx
import re
from bs4 import BeautifulSoup
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def get_title_from_url(url):
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text.strip()
        return title
    except Exception as e:
        print(f"Error fetching title for {url}: {e}")
        return "Could not fetch title"

def get_m3u8_link(url):
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        match = re.search(r'https?://[^"\s]+(?:\.m3u8)', response.text)
        if match:
            return match.group(0)
        else:
            return None
    except httpx.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    url = ""
    title = get_title_from_url(url)
    m3u8_link = get_m3u8_link(url)
    if title:
        print(f"Title: {title}")
    if m3u8_link:
        print(f"Found .m3u8 link: {m3u8_link}")
    else:
        print("No .m3u8 link found.")