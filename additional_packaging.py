#
# SPDX-FileCopyrightText: 2021 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-8-2021
#
#

import os
import glob
import shutil
import logging
from pathlib import Path
import requests 
import tarfile 
from tempfile import NamedTemporaryFile

def additional_packaging(ta_name=None,outputdir="output"):
    noshipdirs = ["aiohttp/.hash"]
    libdir = os.path.join(outputdir,ta_name,"lib")
    for nsd in noshipdirs:
        try:
            o = os.path.join(libdir,nsd)
            # Glob can return FileNotFoundError exception if no match
            logging.info(f"  removing directory {o} from output must not ship")
            shutil.rmtree(o)
        except FileNotFoundError:
            pass

    p = "geoipupdate_4.8.0_linux_amd64"
    url = f'https://github.com/maxmind/geoipupdate/releases/download/v4.8.0/{p}.tar.gz'
    
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        f = NamedTemporaryFile(delete=False)
        f.write(response.raw.read())
        f.close()

        # open file 
        file = tarfile.open(f.name)     
        # extracting file 
        file.extractall('output/SecKit_SA_geolocation/bin/geoipupdate/')     
        file.close() 
        os.rename(f"output/SecKit_SA_geolocation/bin/geoipupdate/{p}","output/SecKit_SA_geolocation/bin/geoipupdate/linux_amd64")
        os.unlink(f.name)