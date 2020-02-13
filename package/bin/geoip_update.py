import import_declare_test
import sys
from builtins import map
from builtins import str
from builtins import range
from splunktalib.conf_manager import conf_manager as conf
from splunktalib import credentials as cred
from splunktalib.common import log
import splunktalib.rest as rest
import splunktalib.common.util as utils
import splunk.clilib.cli_common as scc

from xml.etree import cElementTree as ET
import csv
import os
import logging
import traceback
import splunk_cluster as sc

utils.remove_http_proxy_env_vars()
logger = log.Logs().get_logger('seckit_sa_geolocation', level=logging.DEBUG)


def construct_url(base_url):
    url_list = []
    order_list = list(map(chr, list(range(65, 91))))
    order_list.append('_1234567890')
    for i in order_list:
        url_list.append(base_url+"?azid="+i)
    return url_list


def run():
    logger.info("Script input start.")
    logger.info("Start reading session key")
    if sys.stdin.closed:
        return
    session_key = sys.stdin.read()
    logger.info("End reading session key")
    splunkd_uri = scc.getMgmtUri()
    server_info = sc.ServerInfo(splunkd_uri, session_key)
    if not server_info.is_shc_member() or server_info.is_captain():
        logger.info(
            "This is a single instance or cluster captain. Run the update.")
        app_name = "SecKit_SA_geolocation"
        conf_name = "seckit_sa_geolocation"
        stanza = "seckit_sa_geolocation_proxy"

        encrypted = "******"
        conf_manager = conf.ConfManager(splunkd_uri=splunkd_uri, session_key=session_key,
                                        owner='-', app_name=app_name)
        conf_manager.reload_conf(conf_name)
        stanza_obj = conf_manager.get_conf(conf_name, stanza)
        config = {
            "username": "",
            "password": "",
            "proxy_url": "",
            "proxy_port": "",
            "proxy_username": "",
            "proxy_password": "",
            "proxy_type": "",
            "proxy_rdns": "",
        }
        if stanza_obj["proxy_enabled"].lower().strip() in ("1", "true", "yes", "t", "y"):
            config["proxy_url"] = stanza_obj["proxy_url"]
            config["proxy_port"] = int(stanza_obj["proxy_port"])
            config["proxy_type"] = stanza_obj["proxy_type"]
            config["proxy_rdns"] = stanza_obj["proxy_rdns"]
            is_encrypted = all(stanza_obj.get(
                k, None) == "******" for k in ("proxy_username", "proxy_password"))
            if is_encrypted:
                logger.info("Decrypting")
                cred_mgr = cred.CredentialManager(session_key=session_key,
                                                  app=app_name, splunkd_uri=splunkd_uri)
                user_creds = cred_mgr.get_clear_password(
                    "seckit_sa_geolocation_proxy")
                proxy_username = user_creds["seckit_sa_geolocation_proxy"]["proxy_username"]
                proxy_password = user_creds["seckit_sa_geolocation_proxy"]["proxy_password"]
                config["proxy_username"] = proxy_username
                config["proxy_password"] = proxy_password
            else:
                if stanza_obj["proxy_username"] is not None and stanza_obj["proxy_password"] is not None:
                    logger.info("Encrypting")

                    config["proxy_username"] = stanza_obj["proxy_username"]
                    config["proxy_password"] = stanza_obj["proxy_password"]

                    cred_mgr = cred.CredentialManager(session_key=session_key,
                                                      app=app_name, splunkd_uri=splunkd_uri)
                    try:
                        new_stanza = {}
                        proxy = {
                            'proxy_username': config["proxy_username"], 'proxy_password': config["proxy_password"]}
                        new_stanza['seckit_sa_geolocation_proxy'] = proxy

                        result = cred_mgr.update(new_stanza)
                        logger.info("Update result:"+str(result))

                        proxy_stanza = config.copy()

                        proxy_stanza['proxy_username'] = encrypted
                        proxy_stanza['proxy_password'] = encrypted

                        success = conf_manager.update_stanza(
                            'seckit_sa_geolocation', 'seckit_sa_geolocation_proxy', proxy_stanza)

                        if not success:
                            logger.error(
                                "ERROR in writing seckit_sa_geolocation conf file.")
                    except Exception:
                        logger.error("ERROR in updating cred stanza")
                        logger.error(traceback.format_exc())

        try:
            try:
                http = rest.build_http_connection(config, timeout=60)
            except Exception:
                logger.error("ERROR in building connection")
                return

            if http is not None:
                url_list = construct_url(base_url)
                item_list = extract_xml(http, url_list)
                file_name = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps',
                                         app_name, 'lookups', 'seckit_sa_geolocation_malware_categories_tmp.csv')
                save_lookup_file(file_name, item_list)
                logger.info("Start the SPL")
                request_url = splunkd_uri + "/services/search/jobs/export"
                args = {
                    "search": "|inputlookup seckit_sa_geolocation_malware_category_lookup_tmp "
                    "|append [inputlookup seckit_sa_geolocation_malware_category_lookup] | dedup title"
                    "|outputlookup seckit_sa_geolocation_malware_category_lookup",
                    "output_mode": "raw"
                }
                response, _ = rest.splunkd_request(
                    splunkd_uri=request_url, data=args, session_key=session_key, method='POST')
                if response.status not in (200, 201):
                    logger.error("The SPL is not executed corretcly.")
                else:
                    logger.info("The SPL is executed correctly.")
            else:
                logger.error("Failed to create http object.")
        except Exception:
            logger.error("ERROR in updating malware category lookup table.")
    else:
        logger.info(
            "This is not the cluster captain. Do not run the malare_category_update.")


if __name__ == "__main__":
    run()
