#!/usr/bin/env bash
source .splunkbase 
source ~/.venv/bin/activate
PACKAGE=$(ls build/package/splunkbase/*)
PACKAGE_ID=$(crudini --get package/default/app.conf id name)
[[ $1 =~ ^v[0-9]*.[0-9]*.[0-9]*$ ]] || export ISPRE=-prerelease
SPLUNKBASE_VERSION=$(echo $1 | sed 's/v//' | sed 's/-develop./develop/g')
echo publish $SPLUNKBASE_VERSION
[ "${ISPRE}" == "-prerelease" ] && SPLUNKBASE_VIS="false" || SPLUNKBASE_VIS="true"
echo uploading package
BASE=https://splunkbase.splunk.com/api/v0.1/app/${SPLUNKBASE_ID}/release/
echo $BASE

    curl -u ${SPLUNKBASE_USERNAME}:${SPLUNKBASE_PASSWORD} \
        --request POST https://splunkbase.splunk.com/api/v1/app/${SPLUNKBASE_ID}/new_release/ \
        -F "files[]=@${PACKAGE}" -F "filename=${PACKAGE_ID}.spl" \
        -F "splunk_versions=${SPLUNKBASE_SPLUNK_VERSION}" \
        -F "visibility=${SPLUNKBASE_VIS}"
    sleep 30
    ITEM=$(curl -u ${SPLUNKBASE_USERNAME}:${SPLUNKBASE_PASSWORD} \
        --request GET $BASE \
        | jq ".[] | select(.name==\"$SPLUNKBASE_VERSION\") | .id")

    echo get $ITEM
    CURRENT=$(curl -u ${SPLUNKBASE_USERNAME}:${SPLUNKBASE_PASSWORD} \
        --request GET $BASE${ITEM}/ \
        | jq )

    NOTES=$(cat CHANGELOG.md | jq -sR)
    NEW=$(echo $CURRENT | jq ".release_notes = $NOTES" | jq -c)
    curl -u ${SPLUNKBASE_USERNAME}:${SPLUNKBASE_PASSWORD} \
        --location \
        --request PUT $BASE${ITEM}/ \
        --header 'Content-Type: application/json' \
        --data-raw "$NEW" | jq

