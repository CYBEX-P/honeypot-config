#!/usr/bin/env python3

import sys
import requests
import json

session = sys.argv[1]

query = json.dumps({
  "query": {
    "bool": {
      "filter": [
       { "term" : {"session" : session }}
      ]
    }
  }
})

headers = {'Content-Type': 'application/json'}

print("Querying elasticsearch. This may take a while")
data = requests.get("http://127.0.0.1:9200/_search?size=10000",
                    data=query, headers=headers)
file_json = data.json()

for hit in sorted(file_json["hits"]["hits"], key=lambda x: x["_source"]["timestamp"]):
    if hit["_source"]["eventid"] == "cowrie.session.connect":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              hit["_source"]["protocol"], "session from",
              hit["_source"]["src_ip"] + " (In or near",
              hit["_source"]["geoip"].get("city_name", "unknown") + ",",
              hit["_source"]["geoip"].get("country_name", "unknown") + ")")
    elif hit["_source"]["eventid"] == "cowrie.login.failed":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              "failed login attempt: [" + hit["_source"]["username"] + \
              ":" + hit["_source"]["password"] + "]")
    elif hit["_source"]["eventid"] == "cowrie.login.success":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              "succeeded login attempt: [" + hit["_source"]["username"] + \
              ":" + hit["_source"]["password"] + "]")
    elif hit["_source"]["eventid"] == "cowrie.command.input":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              hit["_source"]["msg"][5:])
    elif hit["_source"]["eventid"] in ("cowrie.command.failed", "cowrie.command.success"):
        # Ignore because this data is in cowrie.command.input
        # print(" "*48 + ":", hit["_source"]["msg"])
        pass
    elif hit["_source"]["eventid"] == "cowrie.session.file_download":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              "file downloaded from " + hit["_source"]["url"], "to",
              hit["_source"]["destfile"])
    elif hit["_source"]["eventid"] == "cowrie.session.closed":
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"] + ":",
              "session ending after", str(hit["_source"]["duration"]), "seconds")
    else:
        print(hit["_source"]["timestamp"], hit["_source"]["eventid"])
