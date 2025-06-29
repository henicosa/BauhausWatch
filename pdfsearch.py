# search for query string in the downloaded protocols and return each result
# with the corresponding protocol, the page number and the position on the page
# as well as a snippet of the text
import re
import os
import json

root_path = "app/"

if not os.path.exists("app/protocols.json"):
    with open("app/protocols.json", "w") as outfile:
        outfile.write("[]")
    print("Created empty app/protocols.json file")

with open("app/protocols.json", "r") as infile:
    protocols = json.load(infile)


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
                text_content = text.read().lower()
                
                # Normalize text and query by removing hyphens for better matching
                normalized_text = text_content.replace('-', '')
                normalized_query = query_string.lower().replace('-', '')
                
                # Search in normalized text
                matches = re.finditer(re.escape(normalized_query), normalized_text)

                for match in matches:
                    # Find the corresponding position in the original text
                    # This is a simplified approach - we'll find the closest match
                    original_pos = match.start()
                    
                    # Adjust for any hyphens we removed
                    hyphen_count_before = text_content[:original_pos].count('-')
                    original_pos += hyphen_count_before
                    
                    # Get the original snippet from the original text
                    snippet_start = max(0, original_pos - 120)
                    snippet_end = min(len(text_content), original_pos + len(normalized_query) + 120)
                    
                    # Highlight the matched text in the original snippet
                    original_snippet = text_content[snippet_start:snippet_end]
                    match_start = original_pos - snippet_start
                    match_end = match_start + len(normalized_query)
                    highlighted_snippet = (
                        original_snippet[:match_start] +
                        "<b>" +
                        text_content[original_pos:original_pos + len(normalized_query)] +
                        "</b>" +
                        original_snippet[match_end:]
                    )
                    
                    match_results.append({
                        "page": int(text_file.split("/")[-1][:-4]) + 1, 
                        "position": original_pos,
                        "snippet": highlighted_snippet,
                        "match_url": (
                            protocol["url"] + "#page=" +
                            text_file.split("/")[-1][:-4] + "&search=" + query_string
                        )
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

