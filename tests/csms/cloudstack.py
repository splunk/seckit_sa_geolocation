#!/bin/env python

from __future__ import print_function
from csmslib.client import Service
import optparse
import getpass
import time
import sys
import urllib3
import json
import datetime

urllib3.disable_warnings()

CLOUD_STACK_CREATE_TIMEOUT=3600

class OptionParser (optparse.OptionParser):
    def check_required (self, opt):
        option = self.get_option(opt)

        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)

parser = OptionParser()
parser.add_option("-o","--operation",dest="operation",help="create | status | info | destroy")
parser.add_option("-t","--stack_type",dest="stack_type",default="sh",help="standalone | sh | shc")
parser.add_option("-i","--stack_id", dest="stack_id",default="",help="stack_id")
parser.add_option("-r","--request_id", dest="request_id",default="",help="request_id")
parser.add_option("-k","--token",dest="token",help="Token to create CSMS stack for SAI")
parser.add_option("-c","--commit",dest="splunk_commit", help="splunk_commit")
parser.add_option("-l","--time_to_live",dest="time_to_live",default=12,help="TTL for cloudtack")

(options, args) = parser.parse_args()

stack_type = options.stack_type
token = options.token
operation = options.operation

if stack_type == "sh":
    stack_type = "cw_cluster"
if stack_type == "shc":
    stack_type = "cw_cluster_shc"
if stack_type == "standalone":
    stack_type = "cw_standalone"

def create_cloudstack(stacks, stack_params):
    stack = stacks.create(stack_params)
    return(stack.stack_id, stack.request_id)

def get_stack_info(stack_id):
    service = Service(token=token)
    service.login()
    stacks = service.stacks
    stack = stacks[stack_id]
    stack_info = json.dumps(stack.stack_info, indent=4, sort_keys=True)
    return stack_info

def destroy_stack(stack_id):
    service = Service(token=token)
    service.login()
    stacks = service.stacks
    status = stacks.terminate(stack_id)
    print(status)

def get_stack_status(request_id):
    service = Service(token=token)
    service.login()
    stacks = service.stacks
    stack = stacks[request_id]
    return stack.stack_status

def create_stack():
    splunk_commit = options.splunk_commit
    time_to_live = options.time_to_live

    stack_params = dict(
        splunk_commit = splunk_commit,
	    stack_type = stack_type,
        speed_up = True,
        time_to_live = time_to_live,
    )

    # Login and create session
    service = Service(token=token)
    service.login()
    stacks = service.stacks

    # Create cloud stack
    (stack_id, request_id) = create_cloudstack(stacks, stack_params)

    print("{0} Creating cloud stack with stack_id {1} and request_id {2}".format(datetime.datetime.now(),stack_id,request_id))
    stack = stacks[request_id]

    # Wait for stack to become available
    timer=0
    while timer <= CLOUD_STACK_CREATE_TIMEOUT:
        if stack.stack_status == 'READY' or stack.stack_status == 'CANCELED':
            break

        print('{0} Waiting for stack [{1}] to become available, current state [{2}]'.format(datetime.datetime.now(), stack.stack_id, stack.stack_status))
        time.sleep(30)
        timer=timer + 30

    if stack.stack_status == 'READY':
        print('{0} Stack is READY to use : {1}'.format(datetime.datetime.now(), stack_id))
        data = {}
        data['stack_id'] = stack_id
        data['admin_user'] = stack.admin_user
        data['admin_password'] = stack.admin_password
        data['sh_url'] = stack.search_heads[0]
        with open('stack.json', 'w') as outfile:
            json.dump(data, outfile)

        return stack_id
    
    if stack.stack_status == 'CANCELED':
        print('{0} stack got canceled by csms admin'.format(stack_id))
    else:
        print('{0} failed to create csms cloud-stack'.format(stack_id))

if operation == "create":   
    stack_id = create_stack()
    print('stack_id:{0}'.format(stack_id))

if operation == "status":
    stack_id = options.stack_id
    stack_status = get_stack_status(stack_id)
    print(stack_status)

if operation == "info":
    stack_id = options.stack_id
    stack = get_stack_info(stack_id)
    print(stack)



if operation == "destroy":
    stack_id = options.stack_id
    destroy_stack(stack_id)