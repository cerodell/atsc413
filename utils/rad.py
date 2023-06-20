#!/Users/crodell/miniconda3/envs/atsc413/bin/python

import context
import json
import sys, os
import requests
import numpy as np
import pandas as pd
from pathlib import Path


def check_file_status(filepath, filesize):
    sys.stdout.write("\r")
    sys.stdout.flush()
    size = int(os.stat(filepath).st_size)
    percent_complete = (size / filesize) * 100
    sys.stdout.write("%.3f %s" % (percent_complete, "% Completed"))
    sys.stdout.flush()
    return


def get_data(filelist, make_dir):
    # Try to get password
    if len(sys.argv) < 3 and not "RDAPSWD" in os.environ:
        try:
            import getpass

            input = getpass.getpass
        except:
            try:
                input = raw_input
            except:
                pass
        pswd = input("Password: ")
    else:
        try:
            pswd = sys.argv[1]
        except:
            pswd = os.environ["RDAPSWD"]

    url = "https://rda.ucar.edu/cgi-bin/login"
    values = {"email": "crodell@eoas.ubc.ca", "passwd": pswd, "action": "login"}
    # Authenticate
    ret = requests.post(url, data=values)
    if ret.status_code != 200:
        print("Bad Authentication")
        print(ret.text)
        exit(1)
    # dspath = "https://rda.ucar.edu"
    dspath = "https://data.rda.ucar.edu"
    for file in filelist:
        filename = dspath + file
        print(filename)
        file_base = str(make_dir) + "/" + os.path.basename(file)
        print("Downloading", file_base)
        req = requests.get(
            filename, cookies=ret.cookies, allow_redirects=True, stream=True
        )
        # filesize = int(req.headers["Content-length"])
        # print(filesize)
        with open(file_base, "wb") as outfile:
            chunk_size = 1048576
            for chunk in req.iter_content(chunk_size=chunk_size):
                outfile.write(chunk)
        #         if chunk_size < filesize:
        #             check_file_status(file_base, filesize)
        # check_file_status(file_base, filesize)
        print()
    return
