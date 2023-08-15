root_path = "app/"

# search for query string in the downloaded protocols and return each result with the corresponding protocol, the page number and the position on the page as well as a snippet of the text
import PyPDF2
import re
import os
import json

protocols = json.load(open("app/protocols.json", "r"))

def search(query_string):
    results = []


    for protocol in protocols:
        # txt directory
        txt_directory = root_path + protocol["local_url"][:-4]

        # get all text files
        text_files = []
        for file in os.listdir(txt_directory):
            if file.endswith(".txt"):
                text_files.append(txt_directory + "/" + file)
        
        match_results = []
        for text_file in text_files:
            # open text file
            with open(text_file, "r") as text:
                text = text.read().lower()

                matches = re.finditer(query_string.lower(), text)

                for match in matches:
                    match_results.append({
                        "page": int(text_file.split("/")[-1][:-4]) + 1, 
                        "position": match.start(),
                        "snippet": text[match.start()-120:match.start()] + "<b>" + text[match.start():match.end()] + "</b>" + text[match.end():match.end()+120],
                        "match_url": protocol["url"] + "#page=" + text_file.split("/")[-1][:-4] + "&search=" + query_string
                    })

        if match_results:
            result = {
                "url": protocol["url"],
                "class": protocol["class"],
                "committee": protocol["committee"],
                "date": protocol["date"],
                "matches": match_results
            }
            results.append(result)

    return results

    # group all results by committee

                    
    # save results to json file
    with open("results.json", "w") as outfile:
        json.dump(results, outfile,
                    sort_keys=True, indent=4,
                    ensure_ascii=False)

