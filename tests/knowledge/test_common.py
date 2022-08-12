# SPDX-FileCopyrightText: 2020 Splunk Inc (Ryan Faircloth) <rfaircloth@splunk.com>
#
# SPDX-License-Identifier: Apache-2.0


def test_positive(record_property, splunk_search_util, seckit_input):

    search = '| makeresults | eval src="8.8.8.8" | `seckit_iplocation(src,src)` | search src_country=US'

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=20, retries=20
    )

    assert result


def test_negative(record_property, splunk_search_util, seckit_input):

    search = '| makeresults | eval src="example.com" | `seckit_iplocation(src,src)` | search NOT src_lat=*'

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=20, retries=20
    )

    assert result


def test_update(record_property, splunk_search_util, seckit_input):

    search = 'search index=_internal source="*/SecKit_SA_geolocation_rh_updater.log" mmdb=GeoLite2-City.mmdb size=*'

    result = splunk_search_util.checkQueryCountIsGreaterThanZero(
        search, interval=20, retries=20
    )

    assert result
