#!/Users/rodell/miniconda3/envs/atsc413/bin/python

import context
import sys, os
import requests
import numpy as np
import pandas as pd
from pathlib import Path

from context import data_dir


#############################  INPUTS  ####################################
## choose case study
case_study = "high_level"
## choose forecast model
model = "gfs"
## choose forecast hour
fh = "00"  # Z (UTC) time
## choose forecast frquency
freq = 3  # in hours

date_range = pd.date_range("2019-05-16", "2019-05-18", freq=f"{freq}H")
############################################################################


make_dir = Path(str(data_dir) + f"/{model}/{case_study}")
make_dir.mkdir(parents=True, exist_ok=True)

int_fct = date_range[0]
fct_hours = np.arange(0, len(date_range) * freq, freq, dtype=int)
filelist = [
    f'/data/ds084.1/{int_fct.strftime("%Y")}/{int_fct.strftime("%Y%m%d")}/gfs.0p25.{int_fct.strftime("%Y%m%d")}{fh}.f{str(fct_hour).zfill(3)}.grib2'
    for fct_hour in fct_hours
]


def check_file_status(filepath, filesize):
    sys.stdout.write("\r")
    sys.stdout.flush()
    size = int(os.stat(filepath).st_size)
    percent_complete = (size / filesize) * 100
    sys.stdout.write("%.3f %s" % (percent_complete, "% Completed"))
    sys.stdout.flush()


# Try to get password
if len(sys.argv) < 2 and not "RDAPSWD" in os.environ:
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
dspath = "https://rda.ucar.edu"

for file in filelist:
    filename = dspath + file
    file_base = str(make_dir) + "/" + os.path.basename(file)
    print("Downloading", file_base)
    req = requests.get(filename, cookies=ret.cookies, allow_redirects=True, stream=True)
    filesize = int(req.headers["Content-length"])
    with open(file_base, "wb") as outfile:
        chunk_size = 1048576
        for chunk in req.iter_content(chunk_size=chunk_size):
            outfile.write(chunk)
            if chunk_size < filesize:
                check_file_status(file_base, filesize)
    check_file_status(file_base, filesize)
    print()
