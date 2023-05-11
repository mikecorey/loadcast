import xml.etree.ElementTree as ET
import requests
import hashlib
import os
from datetime import datetime

from tqdm import tqdm


SOURCES_FILE = os.getenv('LOADCAST_SOURCES_FILE') or './sources.txt'

if os.getenv('LOADCAST_DOWNLOAD_MAX'):
    MAX_EPISODES = int(os.getenv('LOADCAST_DOWNLOAD_MAX'))
else:
    MAX_EPISODES = 5

DOWNLOADED_FILES_DESTINATION = os.getenv('LOADCAST_DOWNLOAD_DIR') or './downloaded/'
PREV_DOWNLOADED_FILES_HASHES = f'{DOWNLOADED_FILES_DESTINATION}/prev_downloaded_files.dat'


def hash_of_url(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def load_an_rss_feed(url):
    shows = []
    r = requests.get(url)
    if r.status_code == 200:
        tree = ET.fromstring(r.content)
        channel_name = tree.find('channel/title').text
        for item in tree.iter('item'):
            title = item.find('title').text
            url = item.find('enclosure').attrib['url']
            description = item.find('description').text
            pub_date_str = item.find('pubDate').text
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
            shows.append({'title': title, 'url': url, 'description': description, 'pub_date': pub_date})
    return shows, channel_name

def check_if_file_exists(url):
    if not os.path.exists(PREV_DOWNLOADED_FILES_HASHES):
        open(PREV_DOWNLOADED_FILES_HASHES, 'w').close()
        return False
    with open(PREV_DOWNLOADED_FILES_HASHES, 'r') as f:
        for line in f:
            if hash_of_url(url) in line:
                return True
    return False


def download_file(url, fn):
    r = requests.get(url)
    if r.status_code == 200:
        with open(fn, 'wb') as f:
            f.write(r.content)
        with open(PREV_DOWNLOADED_FILES_HASHES, 'a') as f:
            f.write(f"{hash_of_url(url)}\n")
        return True
    return False


def main():
    podcasts = {}
    with open(SOURCES_FILE) as f:
        for line in f:
            shows, channel_name = load_an_rss_feed(line.strip())
            podcasts[channel_name] = shows
    for p in podcasts:
        print(f"Syncing: {p}")
        sub_directory = p.replace(' ', '_')[:64]
        os.makedirs(f'{DOWNLOADED_FILES_DESTINATION}{sub_directory}', exist_ok=True)
        for s in tqdm(sorted(podcasts[p], key=lambda x: x['pub_date'], reverse=True)[:MAX_EPISODES]):
            url = s['url']
            new_title = f"{str(s['pub_date'].date())}"
            fqfn = f"{DOWNLOADED_FILES_DESTINATION}{sub_directory}/{new_title.replace(' ', '_')}.mp3"
            if not check_if_file_exists(url):
                success = download_file(url, fqfn)
                if success:
                    #removed manage id3 data.
                    pass


if __name__ == '__main__':
    main()
