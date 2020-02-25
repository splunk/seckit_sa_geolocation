#!/bin/bash

# Getting latest app-itsi build from develop
build_url="https://github.com/splunk/seckit_sa_geolocation/releases/download/v5.0.4/SecKit_SA_geolocation-5.0.4.tar.gz"

target_host=`jq -r .sh_url stack.json`
stack_type='SH'

python tests/csms/app_install.py -o install -u $build_url -g $target_host -s "$stack_type"