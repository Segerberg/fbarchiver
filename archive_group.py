# coding=utf8
import requests
import json
from datetime import datetime
import os
import config
import sys
from multiprocessing import Pool
import logging
import xxhash

"""
A simple library to archive a Facbook group and associated media files.

Configuration (app_secret etc) should be added in a config.py
file in the script folder (see readme).

Media of linked youtube files and other web pages is not archived.
"""

#TODO: Gör till riktig modul istf globala variabler
#TODO: Riktig loggning
#TODO: Grundläggande gruppinfodata.

graph = dict()
graph["data"] = []
outfolder = ""
VERSION = "0.1"
starttime = datetime.now()
paging_limit = 25



def set_up_output_dir(basedir, folder_name):
    """Create ouput folder"""
    global outfolder
    if not os.path.exists(os.path.join(basedir, folder_name)):
        os.makedirs(os.path.join(basedir, folder_name))

    outfolder = os.path.join(basedir, folder_name)



def download_file(linkpair):
    """Download large binary files safely"""
    global outfolder

    url = linkpair[0]
    local_filename = linkpair[1]

    logging.info("Requesting binary file: %s" % url)

    r = requests.get(url, stream=True)

    filepath = os.path.join(outfolder, "media", local_filename)
    logging.info("Writing to %s" % filepath)

    # Calculate file checksum
    hashv = xxhash.xxh64()

    with open(filepath, 'wb') as f:
        # handle download of large files in chunks
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
                hashv.update(chunk)

    logging.info("Wrote binary file: %s, xxhash: %s" % (filepath, hashv.hexdigest()))

    return filepath


def add_archive_metadata():
    global graph

    graph["X-FA_script_version"] = VERSION
    graph["X-FA_start_time"] = starttime
    graph["X-FA_group_id"] = group_id
    graph["X-FA_config_fields"] = config.fields
    
def since_handler():
    since = calendar.timegm(time.strptime(config.since, '%d/%m/%Y'))
    return since


def load_graph(group_id):

    url = "https://graph.facebook.com/v2.4/%s/feed?fields=%s&since=%s&limit=%s&access_token=%s" % (group_id, config.fields,since_handler(), paging_limit, config.access_token)

    load_json(url)




def load_json(url):
    global graph

    try:
        logging.info("Loading %s" % url)

        r = requests.get(url)
        resultjson = r.json()

        graph["data"].extend(resultjson["data"])

        print_stats()

        # load rest of paged data
        if resultjson.has_key("paging") and resultjson["paging"].has_key("next"):
            logging.info("Next page: %s" % resultjson["paging"]["next"])
            load_json(resultjson["paging"]["next"])

    except:
        logging.error(sys.exc_info()[0])




def get_filetype(url):
    """Get content type of file served at <url>."""
    r = requests.head(url)
    if "Content-Type" in r.headers:
        return r.headers["Content-Type"].split("/")[1]
    else:
        return "unknown"


def hydrate_media():
    """
    Fetch binary files in graph data. Adds the local path to
    properties beginning with X-FA_. """

    if config.hydrate_media == False:
        #skip media harvesting
        logging.info("Skipping media files in this harvest (config.hydrate_media = False)")
        return

    fileslist = []
    for post in graph["data"]:
        if post.has_key("full_picture"):
            local_filename = "image_%s.%s" % (post["id"], get_filetype(post["full_picture"]))
            fileslist.append((post["full_picture"], local_filename))
            post["X-FA_full_picture"] = local_filename

        if post.has_key("source") and "https://video." in post["source"]:
            local_filename = "video_%s.%s" % (post["id"], get_filetype(post["source"]))
            fileslist.append((post["source"], local_filename))
            post["X-FA_source"] = local_filename

    logging.info("Found %s files to download" % len(fileslist))

    # set up output directory for media files
    if not os.path.exists(os.path.join(outfolder,"media")):
        logging.info("Creating destination dir: %s" % os.path.join(outfolder,"media"))
        os.makedirs(os.path.join(outfolder,"media"))

    #batch download in parallel
    p = Pool(4)
    p.map(download_file, fileslist)



def archive_group(group_id):
    global outfolder

    # load graph data
    load_graph(group_id)

    # get associated media files (pics + videos)
    hydrate_media()

    # save data file
    with open(os.path.join(outfolder, "archive_%s.json" % group_id), 'wb') as fp:
        logging.info("Writing JSON to %s" % os.path.join(outfolder, "archive_%s.json" % group_id))
        json.dump(graph, fp)
        logging.info("Done!")


def print_stats():
    """Print graph data stats"""

    logging.info("Post count: %s" % len(graph["data"]))


def setup_logging(outfile):
    logging.basicConfig(filename=outfile,level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s:%(levelname)-8s %(message)s')

    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


if __name__ == "__main__":

    #TODO: check if token is available
    if config.access_token:
        starttime = datetime.now()
        group_id = sys.argv[1]


        # Output destination
        output_folder_name = "%s_%s" % (group_id, datetime.now().strftime('%Y%m%d_%H%M%S'))
        set_up_output_dir(config.data_dir, output_folder_name)

        setup_logging(os.path.join(outfolder, group_id + ".log"))

        logging.info("Archiving group %s" % group_id)

        archive_group(group_id)
        logging.info("Ending this run")
    else:
        print "Error: Please add an access token in config.py"
