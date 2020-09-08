import json
import os 
import sys

file_name = "data_for_amcrest.json"

with open(os.path.join(sys.path[0], file_name)) as file:
    jsonfile = json.load(file)

jsonfile["SceneCollections"] = {"Living room Amcrest":{"scene":"preset"}}
jsonfile["SceneCollections"].update({"Another collection":{}})

with open(os.path.join(sys.path[0], file_name), "w") as file:
    json.dump(jsonfile, file, indent=4)

print(json.dumps(jsonfile, indent=4))