#!/usr/bin/env python3

import hashlib
import json
#from virus_total_apis import PublicApi
import sys
from glob import glob
import subprocess
import datetime
import time

print(time.ctime())

folder_path = sys.argv[1]

files = glob(folder_path + "/*")
with open("filelog", "w") as filelog:
    for file in files:
        ftype = " ".join(str(subprocess.check_output(["file", file])).split(":")[1:])
        if "empty" not in ftype:
            filelog.write(file + "||" + ftype + "\n")

print(time.ctime())
