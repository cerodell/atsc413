"""
define the path to important folders without having
 to install anything -- just do:

import contenxt

then the path for the data directory is

context.data_dir

"""
import sys
import site
from pathlib import Path

path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
root_dir = this_dir.parents[0]
data_dir = root_dir / Path("data")
# data_dir = "/Volumes/WFRT-Ext22/atsc413/data"
json_dir = root_dir / Path("json")
# img_dir = root_dir / Path("img")  ## local img dir
img_dir = root_dir / Path("docs") / Path("img")  ## local img dir

# home = str(Path.home())


sys.path.insert(0, str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n")


print(f"through {__file__} -- pha")