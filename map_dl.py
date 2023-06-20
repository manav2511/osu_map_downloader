import re
import argparse
from zipfile import ZipFile
import tempfile
from os.path import basename
from pathlib import Path
import asyncio
import aiohttp
import aiofile
import time

import requests
from tqdm.asyncio import tqdm

start_time = time.time()

async def get_status_code(url, session, sema):
    try:
        async with sema:
            resp = await session.head(url, allow_redirects=True, timeout=10)
            async with resp:
                status_code = resp.status
                url = resp.url

                return (status_code, str(url))
    # Meh
    except:
        return (-1, url)

async def fetch_file(url, path, filename, session, sema):
    async with sema:
        async with session.get(url) as resp:
            data = await resp.read()

    filepath = path.joinpath(filename)
    async with aiofile.async_open(
        filepath, "wb"
    ) as outfile:
        await outfile.write(data)

    return filepath

async def getIdsFromLinks(links, session):
    reg_beatmapset = re.compile(r'(?<=beatmapsets\/)([0-9]*)(?=#|\n|)') # matches format /beatmapsets/xxxxx#xxxxx or /beatmapsets/xxxxx
    reg_beatmap = re.compile(r'(.*\/b\/.*)') # matches format /b/xxxxx

    ids = []

    print("Gettings beatmapset IDs...")

    for i in re.findall(reg_beatmapset, links):
        print(re.findall(reg_beatmapset, links))
        ids.append(i)

    reg_beatmap_found = re.findall(reg_beatmap, links)

    if len(reg_beatmap_found) > 0:
        for url in tqdm(reg_beatmap_found, unit='beatmaps', total=len(reg_beatmap_found)):
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)

                ids.append(re.findall(reg_beatmapset, r.url)[0])
            except:
                print("{} is not a valid beatmap URL!".format(url))
    
    if len(ids) == 0:
        prefix = 'https://osu.ppy.sh/b/'
        beatmap_ids = links.split('\n')
        for beatmap_id in tqdm(beatmap_ids, unit='beatmaps', total=len(beatmap_ids)):
            url = prefix + beatmap_id
            try:
                r = requests.head(url, allow_redirects=True, timeout=10)
                ids.append(re.findall(reg_beatmapset, r.url)[0])
            except Exception as e:
                print(e)
                print("{} is not a valid beatmap URL!".format(url))

    # Async code has some seemingly random issues right now
    # sema = asyncio.BoundedSemaphore(5)
    # tasks = [get_status_code(url, session, sema) for url in reg_beatmap_found]
    # responses = await tqdm.gather(*tasks, unit='beatmaps', total=len(tasks))
    # for resp in responses:
    #     if resp[0] == 200:
    #         ids.append(re.findall(reg_beatmapset, resp[1])[0])
    #     else:
    #         print("{} is not a valid beatmap URL!".format(resp[1]))
    
    # if len(ids) == 0:
    #     prefix = 'https://osu.ppy.sh/b/'
    #     beatmap_ids = links.split('\n')

    #     print([prefix + id for id in beatmap_ids])

    #     tasks = [get_status_code(prefix + id, session, sema) for id in beatmap_ids]
    #     responses = await tqdm.gather(*tasks, unit='beatmaps', total=len(tasks))
    #     for resp in responses:
    #         if resp[0] == 200:
    #             ids.append(re.findall(reg_beatmapset, resp[1])[0])
    #         else:
    #             print("{} is not a valid beatmap URL!".format(resp[1]))

    return ids

async def download(ids, path, session):
    sema = asyncio.BoundedSemaphore(4)

    mirrors = [{
        "name": "chimu.moe",
        "url": "https://api.chimu.moe/v1/download/{}?n=0"
    },
    {
        "name": "beatconnect.io",
        "url": "https://beatconnect.io/b/{}"
    }]

    print("Downloading {} maps".format(len(ids)))

    # tip for download getting stuck
    print("Press Ctrl + C if the download gets stuck")

    # create file list with name and url
    files = [{
        "name": id + ".osz", 
        "url": mirrors[0]["url"].format(id)
    } for id in ids]

    # tqdm.asyncio.tqdm.as_completed()
    # tqdm.gather(*flist)

    # dled = {}

    # print(files[0]["url"], path, files[0]["name"], sema)

    # download the beatmap files
    tasks = [fetch_file(file["url"], path, file["name"], session, sema) for file in files]
    downloaded = await tqdm.gather(*tasks, unit='beatmaps', total=len(tasks))

    # for id in ids:
    #     success = False

    #     # iterate through all available mirrors and try to download the beatmap
    #     for m in mirrors:
            
    #         print("\nTrying to download #{0} from {1}".format(id, m))

            

    #         # download the beatmap file
    #         name = id + ".osz"
    #         filename = path.joinpath(name)

    #         resp = requests.get(url, stream=True, headers=headers)
    #         if resp.status_code == 200:
    #             total = int(resp.headers.get('content-length', 0))

    #             with open(filename, 'wb') as file, tqdm(
    #                 desc=name,
    #                 total=total,
    #                 unit='iB',
    #                 unit_scale=True,
    #                 unit_divisor=1024,
    #             ) as bar:
    #                 for data in resp.iter_content(chunk_size=1024):
    #                     size = file.write(data)
    #                     bar.update(size)

    #             dled.append(filename)

    #             if filename.exists():
    #                 print("Downloaded #{}".format(id))
    #                 success = True

    #             break
        
    #     # print fail message if none of the mirrors work or if download didn't complete
    #     if not success:
    #         print("Failed to download #{}! It probably does not exist on the mirrors.\n"
    #         "Please manually download the beatmap from osu.ppy.sh!".format(id))
    
    print("Finished downloading!")

    #Add all files to zip
    #add_to_zip(dled, name)

    # cleanup temp_dir when done
    # try: temp_dir.cleanup() 
    # except: pass

    return downloaded

    

def add_to_zip(paths, name):
    print("Adding to zip....")

    with ZipFile(name, 'w') as z, tqdm(
        desc=name,
        total=len(paths),
        unit='files',
        unit_scale=True
        ) as bar:
        for f in paths:
            z.write(f, basename(f))
            bar.update()

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


async def main():
    # Read ids from file
    file = args["file"]
    with open(file) as f:
        links = f.read()

    # use temp_dir if no path specified
    if len(args["out"]) == 0:
        temp_dir = tempfile.TemporaryDirectory()
        print("Using temporary directory {}".format(temp_dir.name))
        path = Path(temp_dir.name)
    else:
        path = Path(path)
        
        if not path.exists(): raise Exception("The specified path {} does not exist!".format(path))

    session = aiohttp.ClientSession()

    ids = await getIdsFromLinks(links, session)

    # Start the download
    downloaded = await download(ids, path, session)

    # Add maps to zip
    add_to_zip(downloaded, args["name"])

    await session.close()
    print("Done!")

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))