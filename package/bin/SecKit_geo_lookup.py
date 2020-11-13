#!/usr/bin/env python
import import_declare_test
import os.path
import csv
import sys
import geoip2.database


""" An adapter that takes an ip as input and produces gelocatin data
    based on the max mind data sets

"""

module_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.abspath(os.path.join(module_dir, os.pardir))
data_path = os.path.join(app_dir, 'data')


def main():

    ipfield = sys.argv[1]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    header = r.fieldnames

    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:

        try:
            city2_file = os.path.join(data_path, 'GeoIP2-City.mmdb')
            city2lite_file = os.path.join(data_path, 'GeoLite2-City.mmdb')
            if (os.path.isfile(city2_file)):
                city2reader = geoip2.database.Reader(city2_file)
            elif (os.path.isfile(city2lite_file)):
                city2reader = geoip2.database.Reader(city2lite_file)
            else:
                city2reader = None

            if not city2reader is None:
                city2response = city2reader.city(result[ipfield])
                result['country'] = city2response.country.iso_code
                result['city'] = city2response.city.name
                result['lat'] = city2response.location.latitude
                result['long'] = city2response.location.longitude
        except geoip2.errors.AddressNotFoundError:
            donothing = ""

        try:
            ct_file = os.path.join(data_path, 'GeoIP2-Connection-Type.mmdb')
            if (os.path.isfile(ct_file)):
                ctreader = geoip2.database.Reader(ct_file)
                ct_response = ctreader.connection_type(result[ipfield])
                result['connection_type'] = ct_response.connection_type
                result['network'] = ct_response.network
        except geoip2.errors.AddressNotFoundError:
            donothing = ""

        try:
            isp_file = os.path.join(data_path, 'GeoIP2-ISP.mmdb')
            if (os.path.isfile(isp_file)):
                ispreader = geoip2.database.Reader(isp_file)
                isp_response = ispreader.isp(result[ipfield])
                result['isp'] = isp_response.isp
                result['isp_ip'] = isp_response.ip_address
                result['isp_asn'] = isp_response.autonomous_system_number
                result['isp_asn_organization'] = isp_response.autonomous_system_organization
        except geoip2.errors.AddressNotFoundError:
            donothing = ""

        try:
            anon_file = os.path.join(data_path, 'GeoIP2-Anonymous-IP.mmdb')
            if (os.path.isfile(anon_file)):
                anonreader = geoip2.database.Reader(anon_file)
                anon_response = anonreader.anonymous_ip(result[ipfield])
                result['is_anonymous'] = anon_response.is_anonymous
                result['is_anonymous_proxy'] = anon_response.is_anonymous_proxy                 
                result['is_anonymous_vpn'] = anon_response.is_anonymous_vpn
                result['is_hosting_provider'] = anon_response.is_hosting_provider
                result['is_legitimate_proxy'] = anon_response.is_legitimate_proxy
                result['is_public_proxy'] = anon_response.is_public_proxy
                result['is_satellite_provider'] = anon_response.is_satellite_provider
                result['is_tor_exit_node'] = anon_response.is_tor_exit_node
        except geoip2.errors.AddressNotFoundError:
            donothing = ""

        w.writerow(result)


main()
