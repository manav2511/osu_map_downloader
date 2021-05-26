# osu! map downloader

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

An osu! beatmap downloader that uses Chimu.moe API to download beatmaps from links stored in a text file and zips them afterwards. I made this because zipping mappools is a pain.

### Prerequisites

Python 3.8+

### Installing

Clone the repository

```
git clone https://github.com/manav2511/osu_map_downloader.git
```

Install dependencies

```
cd osu_map_downloader
pip3 install pipenv
pipenv install 
pipenv run python3 map_dl.py -f example.txt -n example.zip
```

## Usage <a name = "usage"></a>

```
map_dl.py [-h] -f example.txt -n example.zip [-o D:\match_pool\]

Download beatmaps from a list of links in a text file.

optional arguments:
  -h, --help            show this help message and exit
  -f pool.txt, --file pool.txt
                        a text file containing beatmap links seperated by newline
  -n example.zip, --name example.zip
                        the name of the zip file to be created
  -o D:\match_pool\, --out D:\match_pool\
                        the directory where downloaded beatmaps are to be saved (make sure the
                        folder exists)
```


