# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment, environment

from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])


def test_isp(record_property, setup_splunk):

    search = "| makeresults | eval src=\"4.5.6.7\" | `seckit_iplocation(src,src)` | search src_isp=\"Level 3 Communications\" | fields - _time | transpose column_name=field include_empty=false 1 | search field=\"src_isp\""

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 1
