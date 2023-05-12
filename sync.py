'''
Loads a list of podcasts from a file and downloads them to a directory.
Author: Mike Corey
'''

import os
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from tqdm import tqdm


SOURCES_FILE = os.getenv('LOADCAST_SOURCES_FILE') or './sources.txt'

if os.getenv('LOADCAST_DOWNLOAD_MAX'):
    MAX_EPISODES = int(os.getenv('LOADCAST_DOWNLOAD_MAX'))
else:
    MAX_EPISODES = 5

DOWNLOADED_FILES_DESTINATION = os.getenv('LOADCAST_DOWNLOAD_DIR') or './downloaded/'
PREV_DOWNLOADED_FILES_HASHES = f'{DOWNLOADED_FILES_DESTINATION}/prev_downloaded_files.dat'

HTTP_TIMEOUT = 60

def hash_of_url(url):
    '''Returns a hash of the url'''
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def load_an_rss_feed(url):
    '''Loads an RSS feed and returns a list of shows'''
    shows = []
    http_response = requests.get(url, timeout=HTTP_TIMEOUT)
    if http_response.status_code == 200:
        tree = ET.fromstring(http_response.content)
        channel_name = tree.find('channel/title').text
        for item in tree.iter('item'):
            title = item.find('title').text
            url = item.find('enclosure').attrib['url']
            description = item.find('description').text
            pub_date_str = item.find('pubDate').text
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
            shows.append(
                {
                    'title': title,
                    'url': url,
                    'description': description,
                    'pub_date': pub_date
                }
            )
    return shows, channel_name


def check_if_file_exists(url):
    '''Checks if a file has been downloaded before'''
    if not os.path.exists(PREV_DOWNLOADED_FILES_HASHES):
        open(PREV_DOWNLOADED_FILES_HASHES, 'w', encoding='utf-8').close()
        return False
    with open(PREV_DOWNLOADED_FILES_HASHES, 'r', encoding='utf-8') as file:
        for line in file:
            if hash_of_url(url) in line:
                return True
    return False


def download_file(url, filename):
    '''Downloads a file and adds it to the list of downloaded files'''
    response = requests.get(url, timeout=HTTP_TIMEOUT)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        with open(PREV_DOWNLOADED_FILES_HASHES, 'a', encoding='utf-8') as file:
            file.write(f"{hash_of_url(url)}\n")
        return True
    return False


def main():
    '''entry point.  This loads a list of podcasts and downloads them'''
    podcasts = {}
    with open(SOURCES_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            shows, channel_name = load_an_rss_feed(line.strip())
            podcasts[channel_name] = shows
    for podcast_name, podcast_data in podcasts.items():
        print(f'Syncing {podcast_name}')
        sub_directory = podcast_name.replace(' ', '_')[:64]
        os.makedirs(f'{DOWNLOADED_FILES_DESTINATION}{sub_directory}', exist_ok=True)
        ordered_podcasts = sorted(podcast_data, key=lambda x: x['pub_date'], reverse=True)
        for show in tqdm(ordered_podcasts[:MAX_EPISODES]):
            url = show['url']
            new_title = f"{str(show['pub_date'].date())}"
            new_title = new_title.replace(' ', '_')
            fqfn = f"{DOWNLOADED_FILES_DESTINATION}{sub_directory}/{new_title}.mp3"
            if not check_if_file_exists(url):
                success = download_file(url, fqfn)
                if success:
                    #removed manage id3 data.
                    pass


if __name__ == '__main__':
    main()
