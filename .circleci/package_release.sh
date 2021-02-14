#!/usr/bin/env bash
##
## SPDX-FileCopyrightText: 2020 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: Apache-2.0
##
##
VERSION=$(echo $1 | sed "s/-develop./develop/g")
echo VERSION="$VERSION" 
source ~/.venv/bin/activate 
ucc-gen --ta-version="$VERSION"

PACKAGE_ID=$(ls output/)
BUILD_DIR=output/$PACKAGE_ID
source ~/.venv/bin/activate
slim generate-manifest $BUILD_DIR --update >/tmp/app.manifest   || true
cp  /tmp/app.manifest  $BUILD_DIR/app.manifest
mkdir -p build/package/splunkbase
mkdir -p build/package/deployment

rm -rf $BUILD_DIR/lib/aiohttp/.hash/
chmod -R -x+X $BUILD_DIR/lib

slim package -o build/package/splunkbase $BUILD_DIR 
mkdir -p build/package/deployment
PACKAGE=$(ls build/package/splunkbase/*)
slim partition $PACKAGE -o build/package/deployment/ || true
slim validate $PACKAGE || true