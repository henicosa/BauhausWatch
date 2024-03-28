import json

path = "protocols.json"

# remove all protocols from the json file with the committee "Studierendenkonvent"

with open(path, "r") as file:
    data = json.load(file)
    data = [protocol for protocol in data if protocol["committee"] != "Studierendenkonvent"]

with open(path, "w") as file:
    json.dump(data, file, indent=4)