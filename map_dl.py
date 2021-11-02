import re
import argparse

from wget import bar_thermometer
try:
    import wget
    wg = True
except:
    wg = False
import requests
from zipfile import ZipFile
import tempfile
from os.path import basename
from pathlib import Path

def getIdsFromLinks(links):
    ra = "(?<=beatmapsets\/)([0-9]*)(?=#|\n)" # matches format /beatmapsets/xxxxx#xxxxx or /beatmapsets/xxxxx
    rb = "(.*\/b\/.*)" # matches format /b/xxxxx

    ids = []

    print("Gettings beatmapset IDs from links..............")

    for i in re.findall(ra, links):
        ids.append(i)

    for url in re.findall(rb, links):
        try:
            r = requests.head(url, allow_redirects=True, timeout=10)

            ids.append(re.findall(ra, r.url)[0])
        except:
            print("{} is not a valid beatmap URL!".format(url))
    
    if len(ids) == 0:
        prefix = 'https://osu.ppy.sh/b/'
        beatmap_ids = links.split('\n')
        for beatmap_id in beatmap_ids:
            url = prefix + beatmap_id
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)
                ids.append(re.findall(ra, r.url)[0])
            except:
                print("{} is not a valid beatmap URL!".format(url))

    return ids

def download(ids, path, name):
    # use temp_dir if no path specified
    if len(path) == 0:
        temp_dir = tempfile.TemporaryDirectory()
        print("Using temporary directory {}".format(temp_dir.name))
        path = Path(temp_dir.name)
    else:
        path = Path(path)
        
        if not path.exists(): raise Exception("The specified path {} does not exist!".format(path)) 

    mirrors = { 
        "beatconnect.io": "https://beatconnect.io/b/{}",
        "chimu.moe": "https://api.chimu.moe/v1/download/{}?n=1"
        }

    dled = []
    for id in ids:
        success = False

        # iterate through all available mirrors and try to download the beatmap
        for m in mirrors:
            url = mirrors[m].format(id)
            print("\nTrying to download #{0} from {1}. Press Ctrl + C if download gets stuck for too long.".format(id, m))

            timeout = False
            
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)
            except:
                timeout = True

            # download the beatmap file
            if not timeout and r.status_code == 200:
                filename = path.joinpath(id + ".osz")

                if wg:
                    wget.download(r.url, out=filename.as_posix())
                else:
                    r = requests.get(r.url)
                    with open(filename, "wb") as f:
                        f.write(r.content)

                dled.append(filename)

                if filename.exists():
                    print("\nDownloaded #{}".format(id))
                    success = True

                break
        
        # print fail message if none of the mirrors work or if download didn't complete
        if not success:
            print("Failed to download #{}! It probably does not exist on the mirrors.\n"
            "Please manually download the beatmap from osu.ppy.sh!".format(id))
    
    print("\nFinished downloading!")

    #Add all files to zip
    add_to_zip(dled, name)

    # cleanup temp_dir when done
    try: temp_dir.cleanup() 
    except: pass

    return dled

def add_to_zip(paths, name):
    print("Adding to zip....")
    with ZipFile(name, 'w') as z:
        for f in paths:
            z.write(f, basename(f))

# Argument parsing
ap = argparse.ArgumentParser(description='Download beatmaps from a list of links.')

ap.add_argument("-f", "--file", required=True, metavar="pool.txt",
   help="a text file containing beatmap links seperated by newline")
ap.add_argument("-n", "--name", required=True, metavar="example.zip",
   help="the name of the zip file to be created")
ap.add_argument("-o", "--out", required=False, metavar="D:\match_pool\\", default="",
   help="the directory where downloaded beatmaps are to be saved, "
   "use this if you don't want the beatmaps to be deleted after zipping (make sure the folder exists)")
args = vars(ap.parse_args())

# Read ids from file
file = args["file"]

with open(file) as f:
    links = f.read()

ids = getIdsFromLinks(links)

#Start the download
dled = download(ids, args["out"], args["name"])

print("Done!")
