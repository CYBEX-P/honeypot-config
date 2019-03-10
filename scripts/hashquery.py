#!/usr/bin/env python3

import sys
import requests
import json

hash = sys.argv[1]

query = json.dumps({
  "query": {
    "bool": {
      "filter": [
       { "term" : {"eventid" : "cowrie.session.file_download"}},
       { "term" : {"shasum" : hash }}
      ]
    }
  }
})

headers = {'Content-Type': 'application/json'}

print("Querying elasticsearch. This may take a while")
data = requests.get("http://127.0.0.1:9200/_search?size=10000",
                    data=query, headers=headers)
file_json = data.json()

response = {"hash" : hash, "total hits" : file_json['hits']['total']}

with open("filelog") as filelog:
    for line in filelog:
        log_json = json.loads(line)
        if log_json["hash"] == hash:
            response["ftype"] = log_json["ftype"]
            response["executable"] = log_json["executable"]

            if response["executable"] == True:
                results = [log_json["full_response"]["scans"][scan]["result"]
                           for scan in log_json["full_response"]["scans"]
                           if log_json["full_response"]["scans"][scan]["result"] != None]

                if sum(["mirai" in scan.lower() for scan in results]) > 3:
                    response["class"] = "mirai"
                elif sum(["shellbot" in scan.lower() for scan in results]) > 3:
                    response["class"] = "shellbot"
                elif sum(["coinminer" in scan.lower() for scan in results]) > 3:
                    response["class"] = "CoinMiner"
                elif sum(["hidenseek" in scan.lower() for scan in results]) >= 1:
                    response["class"] = "HideNSeek"
                elif sum(["downloader" in scan.lower() for scan in results]) > 3:
                    response["class"] = "Downloader script (unknown malware)"
                elif sum(["pnscan" in scan.lower() for scan in results]) > 3:
                    response["class"] = "PNScan"
                elif sum(["ganiw" in scan.lower() for scan in results]) > 3:
                    response["class"] = "Ganiw"
                elif sum(["chinaz" in scan.lower() for scan in results]) > 3:
                    response["class"] = "ChinaZ"
                elif sum(["xorddos" in scan.lower() for scan in results]) > 3:
                    response["class"] = "Xorddos"
                elif sum(["ddostf" in scan.lower() for scan in results]) > 3:
                    response["class"] = "DdosTf"
                else:
                    response["class"] = results

response["hits"] = []

for hit in sorted(file_json['hits']['hits'], key=lambda x:x["_source"]['timestamp']):
    response["hits"].append({"ip" : hit["_source"]['src_ip'],
                             "url" : hit["_source"]['url'],
                             "honeypot" : hit["_source"]['beat']['hostname'],
                             "time" : hit["_source"]['timestamp'],
                             "session" : hit["_source"]["session"]})

print("File type:", response["ftype"])
if "class" in response:
    print("Virustotal report indicates this file is:", response["class"])
for hit in response["hits"]:
    print(hit)
