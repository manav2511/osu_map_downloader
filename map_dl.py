import re
import argparse
import requests
from zipfile import ZipFile

def download(ids, path):
    dled = []
    for id in ids:
        url = "https://api.chimu.moe/v1/download/{0}?n=1".format(id)

        r = requests.get(url, allow_redirects=True)  # to get only final redirect url

        if r.status_code == 200:
            d = r.headers.get("Content-Disposition")
            filename = requests.utils.unquote(re.findall("filename=\"(.+)\"", d)[0])

            filename = path + filename

            with open(filename, "wb") as f:
                f.write(r.content)

            dled.append(filename)

            print("Downloaded #{}".format(id))
        else:
            print("Failed to download #{}! It probably does not exist on the mirror or some error ocurred. \
                    Please manually download the beatmap!".format(id))

    
    print("Finished downloading!")

    return dled

def add_to_zip(paths, name):
    print("Adding to zip....")
    with ZipFile(name, 'w') as z:
        for f in paths:
            z.write(f)

# Argument parsing
ap = argparse.ArgumentParser(description='Download beatmaps from a list of links.')

ap.add_argument("-f", "--file", required=True, metavar="example.txt",
   help="a text file containing beatmap links seperated by newline")
ap.add_argument("-n", "--name", required=True, metavar="example.zip",
   help="the name of the zip file to be created")
ap.add_argument("-o", "--out", required=False, metavar="D:\match_pool\\", default="",
   help="the directory where downloaded beatmaps are to be saved (make sure the folder exists)")
args = vars(ap.parse_args())

# Read ids from file
file = args["file"]

with open(file) as f:
    links = f.read()

ids = re.findall("(?<=beatmapsets\/)(.*)(?=#)", links)

#Start the download
dled = download(ids, args["out"])

#Add all files to zip
add_to_zip(dled, args["name"])

print("Done!")
