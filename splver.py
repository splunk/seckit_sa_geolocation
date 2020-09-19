# coding=utf8
#
# SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
# SPDX-License-Identifier: LicenseRef-Splunk-1-2020
#
#
from __future__ import print_function
import sys

import re

#regex = r'v([0-9]+\.[0-9]+\.[0-9]+)(?:-([abr][a-z]*|d).*(?:\+|\.)(.*))?'
regex = r"v([0-9]+\.[0-9]+\.[0-9]+)(?:-(a|b|r|d).*(?:\+|\.)(.*))?"
test_str = sys.argv[1]

subst = "\\1\\2\\3"
try:
    result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
except:
    result = re.sub(regex, "\\1", test_str, 0, re.MULTILINE)

if result:
    print(result)
