# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause



def test_isp(record_property, splunk_search_util,seckit_input):

    search = "| makeresults | eval src=\"8.8.8.8\" | `seckit_iplocation(src,src)` | search src_country=US"

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=20, retries=20
    )

    assert result


def test_update(record_property, splunk_search_util, seckit_input):



    search = 'search index=_internal source="*SecKit_SA_geolocation_input.log" mmdb=GeoLite2-City.mmdb size=*'

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=20, retries=20
    )

    assert result
