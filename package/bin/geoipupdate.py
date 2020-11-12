import import_declare_test
import sys
import json
import os
import os.path as op
import time
import datetime
import tempfile
import subprocess
import traceback
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from subprocess import CalledProcessError

APP_NAME = __file__.split(op.sep)[-3]
CONF_NAME = "seckit_sa_geolocation"

def get_proxy_settings(session_key, logger):
    """
    This function fetches proxy settings
    :param session_key: session key for particular modular input.
    :param logger: provides logger of current input.
    :return : proxy settings
    """

    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-{}_settings".format(APP_NAME,CONF_NAME))
        ta_settings_conf = settings_cfm.get_conf(
            CONF_NAME+"_settings").get_all()
    except Exception:
        logger.error("Failed to fetch proxy details from configuration. {}".format(
            traceback.format_exc()))
        sys.exit(1)

    proxy_settings = {}
    proxy_stanza = {}
    for key, value in ta_settings_conf["proxy"].items():
        proxy_stanza[key] = value

    if int(proxy_stanza.get("proxy_enabled", 0)) == 0:
        return proxy_settings
    proxy_port = proxy_stanza.get('proxy_port')
    proxy_url = proxy_stanza.get('proxy_url')
    proxy_username = proxy_stanza.get('proxy_username', '')
    proxy_password = proxy_stanza.get('proxy_password', '')

    if proxy_username and proxy_password:
        proxy_username = rq.compat.quote_plus(proxy_username)
        proxy_password = rq.compat.quote_plus(proxy_password)
        proxy_uri = "%s://%s:%s@%s:%s" % (proxy_type, proxy_username,
                                          proxy_password, proxy_url, proxy_port)
    else:
        proxy_uri = "%s://%s:%s" % (proxy_type, proxy_url, proxy_port)

    proxy_settings = {
        "http": proxy_uri,
        "https": proxy_uri,
        "username": proxy_username,
        "proxy_password": proxy_password,
        "proxy": proxy_url,
        "proxy_port": proxy_port

    }
    logger.info("Fetched configured proxy details.")
    return proxy_settings


def get_log_level(session_key, logger):
    """
    This function returns the log level for the addon from configuration file.
    :param session_key: session key for particular modular input.
    :return : log level configured in addon.
    """
    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-{}_settings".format(APP_NAME,CONF_NAME))

        logging_details = settings_cfm.get_conf(
            CONF_NAME+"_settings").get("logging")

        log_level = logging_details.get('loglevel') if (
            logging_details.get('loglevel')) else 'INFO'
        return log_level

    except Exception:
        logger.error(
            "Failed to fetch the log details from the configuration taking INFO as default level.")
        return 'INFO'

def get_account_details(session_key, account_name, logger):
    """
    This function retrieves account details from addon configuration file.
    :param session_key: session key for particular modular input.
    :param account_name: account name configured in the addon.
    :param logger: provides logger of current input.
    :return : account details in form of a dictionary.    
    """
    try:
        cfm = conf_manager.ConfManager(
            session_key, APP_NAME, realm='__REST_CREDENTIAL__#{}#configs/conf-{}_account'.format(APP_NAME,CONF_NAME))
        account_conf_file = cfm.get_conf(CONF_NAME + '_account')
        logger.info(f"Fetched configured account {account_name} details.")
        return {
            "username": account_conf_file.get(account_name).get('username'),
            "password": account_conf_file.get(account_name).get('password'),
        }
    except Exception as e:
        logger.error("Failed to fetch account details from configuration. {}".format(
            traceback.format_exc()))
        sys.exit(1)


class GEOIPUPDATE(smi.Script):

    def __init__(self):
        super(GEOIPUPDATE, self).__init__()

    def get_scheme(self):
        scheme = smi.Scheme('geoipupdate')
        scheme.description = 'geoipupdate'
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = True

        scheme.add_argument(
            smi.Argument(
                'name',
                title='Name',
                description='Name',
                required_on_create=True
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'interval',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'edition_ids',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'global_account',
                required_on_create=True,
            )
        )
        
        return scheme

    def validate_input(self, definition):
        return

    def stream_events(self, inputs, ew):
        meta_configs = self._input_definition.metadata
        session_key = meta_configs['session_key']
        
        input_items = {}
        input_name = list(inputs.inputs.keys())[0]
        input_items = inputs.inputs[input_name]
        
        # Generate logger with input name
        _, input_name = (input_name.split('//', 2))
        logger = log.Logs().get_logger(
            '{}_input'.format(APP_NAME))

        # Log level configuration
        log_level = get_log_level(session_key, logger)
        logger.setLevel(log_level)

        logger.debug("Modular input invoked.")

        try:
            account_name = input_items.get('global_account')
            account_details = get_account_details(
                session_key, account_name, logger)
            
            username = account_details.get('username')
            password = account_details.get('password')
            if not username:
                logger.error(
                    "Username is required {} to resume updates".format(account_name))
                sys.exit(1)
            if not password:
                logger.error(
                    "password is required {} to resume updates".format(account_name))
                sys.exit(1)
            
            logger.debug(f"username is {username}")
            # Proxy configuration
            proxy_settings = get_proxy_settings(session_key, logger)

            edition_ids = input_items.get('edition_ids')
                    
            with tempfile.NamedTemporaryFile(mode='w', suffix=".conf", prefix="GeoIP") as file:
                    file.write("\nAccountID " + username)
                    file.write("\nLicenseKey " + password)
                    file.write("\nEditionIDs " + edition_ids + "\n")

                    if proxy_settings == {}:
                        logger.debug("no proxy")
                    else:
                        file.write(
                            "\nProxy " + proxy_settings["proxy_url"] + ":" + proxy_settings["proxy_port"])
                        if not proxy_settings["proxy_username"] is None:
                            file.write(
                                "\nProxyUserPassword " + proxy_settings["proxy_username"] + ":" + proxy_settings["proxy_password"])

                    file.flush()
                    guargs = str(os.path.expandvars(
                        "-v -d $SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/ -f " + file.name))

                    try:
                        subprocess.check_output(
                        ["$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoipupdate/linux_amd64/geoipupdate " + guargs], shell=True,stderr=subprocess.STDOUT)
                    except CalledProcessError as e:
                        logger.exception(e)
                        logger.error("command args:\n")
                        logger.error(e.cmd)
                        logger.error("output:\n")
                        logger.error(e.output.decode("utf-8") )
                        sys.exit(1)

                    mmdb_dir = os.path.expandvars(
                        '$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/')
                    files = os.listdir(mmdb_dir)
                    for name in files:
                        if name.endswith('.mmdb'):
                            inode = os.stat(os.path.join(mmdb_dir, name))
                            logger.info(
                                'mmdb=' + name + ' size=' +
                                str(inode.st_size) + ' mtime=' + str(inode.st_mtime)
                            )
        except Exception as e:
            logger.exception(e)
            sys.exit(1)
        

        logger.debug("Modular input completed")
if __name__ == '__main__':
    exit_code = GEOIPUPDATE().run(sys.argv)
    sys.exit(exit_code)