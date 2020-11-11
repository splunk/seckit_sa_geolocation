# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause



def test_isp(record_property, splunk_search_util):

    search = "| makeresults | eval src=\"4.5.6.7\" | `seckit_iplocation(src,src)` | search src_isp=\"Level 3 Communications\" | fields - _time | transpose column_name=field include_empty=false 1 | search field=\"src_isp\""

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=1, retries=1
    )

    assert result


def test_update(record_property, splunk_search_util, seckit_input):



    search = 'search index=_internal source="/opt/splunk/var/log/splunk/splunkd.log" "Acquired lock file lock"'

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=10, retries=18
    )

    assert result
