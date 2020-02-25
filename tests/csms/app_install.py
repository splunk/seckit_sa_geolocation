#!/bin/env python

import requests
import json
import argparse
import time
import sys

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Splunk app installation on CSMS cloudstack")
parser.add_argument('-o','--operation', type=str, help='install or status')
parser.add_argument('-u','--app_url', type=str, help='url of app to install')
parser.add_argument('-g','--target_host', type=str, help='hostname to install app')
parser.add_argument('-i','--stack_id', type=str, help='csms cloudstack id')
parser.add_argument('-t','--token', type=str, help='app_install token')
parser.add_argument('-s','--stack_type', type=str, help='SH, SHC or IDX')
parser.add_argument('-r','--app_install_request_id', type=str, default="", help="app_install_request_id")
args = parser.parse_args()



app_install_token = args.token
operation = args.operation
app_url = args.app_url
target_host = args.target_host
stack_id = args.stack_id
stack_type = args.stack_type
app_install_request_id = args.app_install_request_id

app_install_service_url="http://app-install.eecqcs.sv.splunk.com/api/v1/appinstallrequest/"
headers = {'content-type': 'application/json', 'Authorization':'token {}'.format(app_install_token)}

def app_install(app_install_token, app_url_ok, stack_id, target_host, stack_type, app_install_service_url):
  app_install_data = {
    'target_host'   : target_host,
    'is_shc'        : False,
    'app_url'       : app_url_ok
  }

  print("Requesting app installation...")
  print(target_host)
  res = requests.post(url=app_install_service_url, data=json.dumps(app_install_data), headers=headers)
  stack_req_res = json.loads(res.text)
  print(stack_req_res)
  app_install_request_id = stack_req_res['request_id']
  return app_install_request_id

def app_install_status(app_install_request_id):
  stack_install_status_res = requests.get(url=app_install_service_url + app_install_request_id + "/", headers=headers)
  install_status_data = json.loads(stack_install_status_res.text)
  install_status = (install_status_data['app_task']['installation_status'])
  return install_status

def wait_for_app_install(app_install_request_id):
  WAIT_TIMEOUT = 300
  timer = 0
  while timer <= WAIT_TIMEOUT:
      install_status = app_install_status(app_install_request_id)
      print(install_status)
      time.sleep(15)
      timer = timer + 15

      if install_status == "APP_INSTALLATION_SUCCESS":
        break
      
      if install_status == "APP_INSTALLATION_FAILED" or install_status == "APP_DOWNLOAD_FAILED":
        print("Failed to install app")
        exit()

  print("Successfully completed installation of app on stack")
  return(install_status)

if app_url:
  app_url_ok = app_url

if operation == "install":
  print("Installing app %s" %(app_url_ok))
  app_install_request_id = app_install(app_install_token, app_url_ok, stack_id, target_host, stack_type, app_install_service_url)
  wait_for_app_install(app_install_request_id)

if operation == "status":
    wait_for_app_install(app_install_request_id)