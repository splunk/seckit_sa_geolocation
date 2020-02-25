#!/bin/env python

from __future__ import print_function
from csmslib.client import Service
from optparse import OptionParser


def login_server():
    # You can also use your AD user/password to login and get self token to manage stack operation.
    parser = OptionParser()
    parser.add_option("-u","--user",dest="user",type="string")
    parser.add_option("-p","--password",dest="password",type="string")


    (options, args) = parser.parse_args()
    user  = str.encode(options.user)
    password = str.encode(options.password)
    service = Service(username=user, password=password)
    service.login()
    print (service.token)

    service.logout()


if __name__ == '__main__':
    login_server()
