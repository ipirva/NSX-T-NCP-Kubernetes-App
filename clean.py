#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
import re
import yaml

file = "nsx_cluster_ncp_config_dump_.json"
fileUpdate = "nsx_cluster_ncp_config_dump.json"

with open(file) as oldfile, open(fileUpdate, 'w') as newfile:
    for line in oldfile:
        if re.search("^\"_.*$", line.strip()) or re.search("\".*time.*:\"$", line.strip()) or re.search("\".*path.*:\"$", line.strip()) or re.search("\"display_name\":.*$", line.strip()):
            pass
        else:
            newfile.write(line)

# get rid of trailing ,
data = yaml.load(open(fileUpdate), Loader=yaml.FullLoader)
data = json.dumps(data, sort_keys=True, indent=4)

with open(fileUpdate, "w") as fileHandler:
    fileHandler.write(data)


