# Loadcast

Loadcast is a simple script to sync your podcasts with your mp3 player. It reads a sources file and downloads the podcasts to a destination folder. It can also be used to sync any other files.

## Usage

`python sync.py`

## Configuration

The configuration is done in the `sources` file. Simply put in the url to a podcast rss feed on each line and it will check that url for new podcasts.

### Environment Variables

`LOADCAST_SOURCES_FILE` - The path to the sources file. Defaults to `./sources.txt`.

`LOADCAST_DOWNLOAD_DIR` - The path to the destination folder. Defaults to `./downloaded`.

`LOADCAST_DOWNLOAD_MAX` - The maximum number of files to download per podcast. Defaults to `5`.
