#!/usr/bin/env python

import hashlib
import json
from virus_total_apis import PublicApi
import code
import sys
import subprocess
import datetime

api_key = "<api key here>"
file_path = sys.argv[1]
ftype = " ".join(subprocess.check_output(["file", file_path]).split(" ")[1:]).strip("\n")


# stackoverflow.com/a/3431838
hash = hashlib.sha256()
with open(file_path, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
        hash.update(chunk)

with open("/home/cybex-user/checked-hashes") as hashlist:
    for line in hashlist:
        if line.split()[0].strip("[]") == hash.hexdigest():
            print("File already checked: " + ftype)
            exit()

line = ""
if "empty" in ftype or "ASCII text" in ftype:
    line = "[" + hash.hexdigest() + "] [" + ftype + "] [-/-] [" + str(datetime.datetime.now()) + "]"
else:
    virustotal = PublicApi(api_key)
    response = virustotal.get_file_report(hash.hexdigest())
    if response["response_code"] == 200:
        if "requested resource is not among the" in response["results"]["verbose_msg"]:
            print(hash.hexdigest() + " " + ftype + " NA/NA " + str(datetime.datetime.now()))
            response = virustotal.scan_file(file_path, from_disk=True, filename=hash.hexdigest())
            with open("/home/cybex-user/debug", "a") as response_dump:
                response_dump.write(response)

        positives = response["results"]["positives"]
        total = response["results"]["total"]
        date = response["results"]["scan_date"]

        line = "[" + hash.hexdigest() + "] [" + ftype + "] [" + str(positives) + "/" + str(total) + "] [" + str(datetime.datetime.now()) + "]"

    else:
        print("Response code:", response["response_code"], ": quota may be exceeded")

with open("/home/cybex-user/checked-hashes", "a") as hashlist:
    hashlist.write(line + "\n")

print(line)
