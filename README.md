# osu! map downloader

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

An osu! beatmap downloader that uses Beatconnect.io and Chimu.moe mirrors to download beatmaps from links stored in a text file and zips them afterwards. I made this because zipping mappools is a pain.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

Python 3

### Installing

Clone the repository

```
git clone https://github.com/manav2511/osu_map_downloader.git
```

Install dependencies

```
cd osu_map_downloader
pip install requests
pip install wget (optional, only run this if you want progress bars)
```

Example 

```
python map_dl.py -f example.txt -n example.zip
```

See [example.txt](example.txt) to understand how to store the links.

## Usage <a name = "usage"></a>

Basic usage

```
python map_dl.py -f links.txt -n zipname.zip
```

Help

```
python map_dl.py [-h] -f example.txt -n example.zip [-o D:\match_pool\]

Download beatmaps from a list of links in a text file.

optional arguments:
  -h, --help            show this help message and exit
  -f example.txt, --file example.txt
                        a text file containing beatmap links seperated by newline
  -n example.zip, --name example.zip
                        the name of the zip file to be created
  -o D:\match_pool\, --out D:\match_pool\
                        the directory where downloaded beatmaps are to be saved,
                        use this if you don't want the beatmaps to be deleted after zipping (make sure the folder exists)
```


