#!/usr/bin/env python3

import requests
import hashlib
from glob import glob
import subprocess
import os
import json
import time
import sys

api_key = "<virustotal-API-key>"

files = glob("new-files/*")
for file in files:
    ftype = subprocess.check_output(["file", file])[len(file)+2:].decode("utf-8").strip("\n")
    print(ftype)
    if ftype != "empty":
        hash = hashlib.sha256()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)

        with open("filelog", "r") as filelog:
            if hash.hexdigest() in [json.loads(line)["hash"] for line in filelog]:
                print("Already checked file", hash.hexdigest())
                os.remove(file)
                continue

        if "executable" in ftype:
            time.sleep(15) # avoid overloading virustotal api quota
            params = {'apikey' : api_key, 'resource' : hash.hexdigest()}
            headers = { "Accept-Encoding": "gzip, deflate" }
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/report',
                                    params=params, headers=headers)
            print(response.text)
            vtotal_json = response.json()

            if "requested resource is not among the" in vtotal_json["verbose_msg"]:
                print("File not in VirusTotal. Uploading, try again later")
                print("File hash:", hash.hexdigest())
                filebinary = {"file" : (hash.hexdigest(), open(file, "rb"))}
                time.sleep(15)
                response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan',
                                         files=filebinary, params={'apikey': api_key})
                continue
            else:
                log_msg = json.dumps({"hash" : hash.hexdigest(), "ftype" : ftype,
                            "executable" : True,
                            "scan_date" : vtotal_json['scan_date'],
                            "total_scans" : vtotal_json['total'],
                            "positives" : vtotal_json['positives'],
                            "full_response" : vtotal_json})

            with open("filelog", "a") as filelog:
                filelog.write(log_msg + "\n")
        else:
            log_msg = json.dumps({"hash" : hash.hexdigest(), "ftype" : ftype,
                        "executable" : False, "scan_date" : "-",
                        "total_scans" : "-", "positives" : "-"})
            with open("filelog", "a") as filelog:
                filelog.write(log_msg + "\n")

        os.rename(file, "checked-files/" + hash.hexdigest())
    else:
        os.remove(file)
