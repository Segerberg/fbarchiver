# coding=utf8
import requests
import json
from datetime import datetime
import os
import config
import sys
from multiprocessing import Pool
from selenium import webdriver

"""
A simple library to archive a Facbook group and associated media files.

Configuration (app_secret etc) should be added in a config.py
file in the script folder (see readme).

Media of linked youtube files and other web pages is not archived.
"""

#TODO: Skriv arkivmetadata X-FA...
#TODO: Gör till riktig modul istf globala variabler
#TODO: Riktig loggning
#TODO: Grundläggande gruppinfodata.

graph = dict()
graph["data"] = []
outfolder = ""
VERSION = "0.1"
starttime = datetime.now()
paging_limit = 1000


def set_up_output_dir(folder_name):
    """Create ouput folder"""
    global outfolder
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    outfolder = folder_name
    print "Destination: " + outfolder



def download_file(linkpair):
    """Download large binary files safely"""
    global outfolder
    url = linkpair[0]
    local_filename = linkpair[1]

    if not os.path.exists(outfolder + "/media"):
        os.makedirs(outfolder + "/media")

    r = requests.get(url, stream=True)

    filepath = os.path.join(outfolder, "media", local_filename)

    with open(filepath, 'wb') as f:
        # handle download of large files in chunks
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    print "Wrote: " + filepath
    return filepath


def add_archive_metadata():
    global graph

    graph["X-FA_script_version"] = VERSION
    graph["X-FA_start_time"] = starttime
    graph["X-FA_group_id"] = group_id
    graph["X-FA_config_fields"] = config.fields



def load_graph(group_id):
    """Load json data for <group_id> and print basic stats."""
    global graph

    url = "https://graph.facebook.com/v2.6/%s/feed?fields=%s&limit=%s&access_token=%s" % (group_id, config.fields, paging_limit, config.access_token)

    load_json(url)




def load_json(url):
    global graph


    try:
        r = requests.get(url)
        resultjson = r.json()

        graph["data"].extend(resultjson["data"])

        print_stats()

        # load rest of paged data
        if resultjson.has_key("paging") and resultjson["paging"].has_key("next"):
            print "loading next page"
            load_json(resultjson["paging"]["next"])

    except:
        print "Error: %s" % sys.exc_info()[0]




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

    print "Files to download: %s" % len(fileslist)

    #batch download in parallel
    p = Pool(4)
    p.map(download_file, fileslist)



def archive_group(group_id):
    # Output destination
    output_folder_name = "%s_%s" % (group_id, datetime.now().strftime('%Y%m%d_%H%M%S'))
    set_up_output_dir(output_folder_name)

    # load graph data
    load_graph(group_id)

    # get associated media files (pics + videos)
    hydrate_media()

    # save data file
    with open(os.path.join(output_folder_name, "archive_%s.json" % group_id), 'wb') as fp:
        json.dump(graph, fp)


def save_snapshot(group_id):
    driver = webdriver.PhantomJS()
    #driver.set_window_size(1024, 768) # optional
    driver.get("https://www.facebook.com/groups/%s/" % group_id)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.save_screenshot('archive_%s.pdf' % group_id) # save a screenshot to disk
    #sbtn = driver.find_element_by_css_selector('button.gbqfba')
    sbtn.click()


def print_stats():
    """Print graph data stats"""

    print "\nPost count: %s" % len(graph["data"])



if __name__ == "__main__":

    #TODO: check if token is available
    if config.access_token:
        starttime = datetime.now()
        group_id = sys.argv[1]
        print "Archiving %s" % group_id
        archive_group(group_id)
    else:
        print "Please add an access token in config.py"
