import re
import argparse
import requests
from zipfile import ZipFile
import tempfile
from os.path import basename

def download(ids, path, name):
    # use temp_dir if no path specified
    if len(path) == 0:
        temp_dir = tempfile.TemporaryDirectory()
        print("Using temporary directory {}".format(temp_dir.name))
        path = temp_dir.name + "\\"

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
            print("Trying to download #{0} from {1}".format(id, m))

            timeout = False
            
            try:
                r = requests.get(url, allow_redirects=True, timeout=10)  # to get only final redirect url
            except:
                timeout = True

            # download the beatmap file
            if not timeout and r.status_code == 200:
                filename = path + id + ".osz"

                with open(filename, "wb") as f:
                    f.write(r.content)

                dled.append(filename)

                print("Downloaded #{}".format(id))
                success = True

                break
        
        # print fail message if none of the mirrors work
        if not success:
            print("Failed to download #{}! It probably does not exist on the mirrors.\n"
            "Please manually download the beatmap from osu.ppy.sh!".format(id))
    
    print("Finished downloading!")

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

ids = re.findall("(?<=beatmapsets\/)(.*)(?=#)", links)

#Start the download
dled = download(ids, args["out"], args["name"])

print("Done!")
