# request url and get all links to a protocol
import requests
import re
from bs4 import BeautifulSoup
import datetime
import locale
import os
import pdfextract

# Set the locale to German
try:
    locale.setlocale(locale.LC_TIME, "de_DE.utf-8")
except locale.Error as e:
    raise RuntimeError(f"Failed setting German local{e}. Please install it with \nsudo apt-get install language-pack-de\nand try again.") from e
    
# download protocols
import urllib.request

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

processed_links = []

def embed_ocr_text(filepath):
    return




def name_to_directory_name(name):
    name = name.replace("/", "_")
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return name.lower().replace(" ", "_")

def get_protocols_from_url(url, committee, class_name):

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    protocols_added = 0

    domain = url.split("/")[2]

    links = []
    for link in soup.find_all("a"):
        links.append(link)

    # filter links to protocols
    protocols = []
    for link in links:
        try:
            protocol = read_protocol_from_url(domain, link, committee, class_name)
        except Exception as e:
            print(e)
            continue

        if protocol is not None:
            print("Found new protocol ", protocol["filename"])
            protocols.append(protocol)

    return protocols


def read_protocol_from_url(domain, link, committee, class_name):
    if link is None or link.get("href") is None:
        return None

    if not link.get("href").startswith("http"):
        href = "https://" + domain + "/" + link.get("href")
    else:
        href = link.get("href")

    if not ".pdf" in href or href in processed_links:
        return None
    
    processed_links.append(href)
    protocol = {
        "date": "Datum unbekannt",
        "unixdate": 0,
        "fetched_date": datetime.datetime.now().strftime("%d.%m.%Y"),
        "fetched_unixdate": datetime.datetime.now().timestamp(),
        "url": href,
        "filename": href.split("/")[-1],
        "link_title": link.text,
        "committee": committee,
        "class": class_name
    }

    filepath = "downloads/" + name_to_directory_name(protocol["committee"]) + "/" + protocol["filename"]
    
    # check if subdirectory exists
    if not os.path.exists("downloads/" + name_to_directory_name(protocol["committee"])):
        os.makedirs("downloads/" + name_to_directory_name(protocol["committee"]))
    
    # check if file already exists
    if not os.path.exists(filepath):
        urllib.request.urlretrieve(protocol["url"], filepath)
        print("Downloaded " + protocol["url"])

    # get date from pdf file
    protocol["date"] = pdfextract.get_protocol_date_from_pdf_file(filepath)

    if protocol["date"] and protocol["date"] != "Datum unbekannt":
        protocol["unixdate"] = datetime.datetime.strptime(protocol["date"], "%d.%m.%Y").timestamp()

    protocol["local_url"] = filepath
    pdfextract.save_protocol_pages_to_txt(filepath)
    return protocol


def update():
    global processed_links

    # check if download folder exists
    import os
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    if not os.path.exists("protocols.json"):
        with open("protocols.json", "w") as outfile:
            outfile.write("[]")
        print("Created empty app/protocols.json file")

    previous_protocols = read_json("protocols.json")
    processed_links  = [proto["url"] for proto in previous_protocols]

    sources = read_json("sources.json")

    protocols = []
    for source in sources:
        print("Load protocols for", source["name"])
        new_protocols = get_protocols_from_url(source['url'], source['name'], source['keyword'])
        protocols += new_protocols
        print("Found new", len(new_protocols) ,"protocols for", source["name"])

    protocols += previous_protocols

    # sort protocols by date
    protocols = sorted(protocols, key=lambda k: k["unixdate"], reverse=True)

    # save protocols to json file
    import json
    
    with open("protocols.json", "w") as f:
        json.dump(protocols, f, indent=4)

if __name__ == "__main__":
    #get_protocols_from_url("https://m18neo.bau-ha.us/m18-archiv/", "Stuko", "uni")
    update()