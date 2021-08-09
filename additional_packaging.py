#
# SPDX-FileCopyrightText: 2021 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-1-2020
#
#

import os
import glob
import shutil
import logging
from pathlib import Path

def additional_packaging(ta_name=None,outputdir="output"):
    noshipdirs = ["aiohttp","requests", "urlib3"]
    p = Path(os.path.join(outputdir,ta_name,"lib","*"))
    for nsd in noshipdirs:
        try:
            # Glob can return FileNotFoundError exception if no match
            for o in p.glob(nsd + "*"):
                if o.is_dir():
                    logging.info(f"  removing directory {o} from output must not ship")
                    shutil.rmtree(o)
        except FileNotFoundError:
            pass