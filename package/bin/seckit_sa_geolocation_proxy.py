import import_declare_test
from builtins import str
import splunk.admin as admin
import splunk.clilib.cli_common as scc
import splunktalib.common.util as utils
from splunktalib import credentials as cred
from splunktalib.conf_manager import conf_manager as conf
from splunktalib.common import log
import logging
import traceback
import os

utils.remove_http_proxy_env_vars()
logger = log.Logs().get_logger('seckit_sa_geolocation', level=logging.DEBUG)
script_path = os.path.join('$SPLUNK_HOME', 'etc', 'apps',
                           'SecKit_SA_geolocation', 'bin', 'geoip_update.py')


"""
Copyright (C) 2005 - 2015 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values 
      corresponds to handleractions = edit in restmap.conf
"""


class ConfigApp(admin.MConfigHandler):

    encrypted = "******"

    """
    Set up supported arguments
    """

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['proxy_enabled', 'proxy_url', 'proxy_port', 'proxy_username', 'proxy_password', 'proxy_type',
                        'proxy_rdns']:
                self.supportedArgs.addOptArg(arg)

    """
    Read the initial values of the parameters from the custom file
      seckit_sa_geolocation.conf, and write them to the setup screen.

    If the app has never been set up,
      uses .../<appname>/default/seckit_sa_geolocation.conf.

    If app has been set up, looks at
      .../local/seckit_sa_geolocation.conf first, then looks at
    .../default/seckit_sa_geolocation.conf only if there is no value for a field in
      .../local/seckit_sa_geolocation.conf

    For boolean fields, may need to switch the true/false setting.

    For text fields, if the conf file says None, set to the empty string.

    """

    def handleList(self, confInfo):
        confDict = self.readConf("seckit_sa_geolocation")
        if confDict is not None:
            self._decrypt_username_password(confDict)
            proxy = confDict['seckit_sa_geolocation_proxy']

            for key, val in list(proxy.items()):
                if key == 'proxy_password':
                    val = ''
                confInfo['seckit_sa_geolocation_proxy'].append(key, val)

    """
    After user clicks Save on setup screen, take updated parameters,
    normalize them, and save them somewhere
    """

    def handleEdit(self, confInfo):
        args = self.callerArgs.data
        for key, val in list(args.items()):
            if val[0] is None:
                val[0] = ''

        proxy_stanza = {}
        proxy_enabled = args['proxy_enabled'][0]
        proxy_stanza['proxy_enabled'] = proxy_enabled
        if proxy_enabled.lower().strip() in ("1", "true", "yes", "t", "y"):
            proxy_port = args['proxy_port'][0].strip()
            proxy_url = args['proxy_url'][0].strip()
            proxy_type = args['proxy_type'][0]
            proxy_rdns = args['proxy_rdns'][0]
            # Validate args
            if proxy_url != '' and proxy_port == '':
                raise admin.ArgValidationException("Port should not be blank")

            if proxy_url == '' and proxy_port != '':
                raise admin.ArgValidationException("URL should not be blank")

            if proxy_port != '' and not proxy_port.isdigit():
                raise admin.ArgValidationException("Port should be digit")

            # Proxy is enabled, but proxy url or port is empty
            if proxy_url == '' or proxy_port == '':
                raise admin.ArgValidationException(
                    "URL and port should not be blank")

            # Password is filled but username is empty
            if args['proxy_password'][0] != '' and args['proxy_username'][0] == '':
                raise admin.ArgValidationException(
                    "Username should not be blank")

            if proxy_type not in ('http', 'http_no_tunnel', 'socks4', 'socks5'):
                raise admin.ArgValidationException("Unsupported proxy type")

            confDict = self.readConf("seckit_sa_geolocation")
            self._decrypt_username_password(confDict)
            proxy = confDict['seckit_sa_geolocation_proxy']

            proxy_stanza['proxy_url'] = proxy_url
            proxy_stanza['proxy_port'] = proxy_port
            proxy_stanza['proxy_type'] = proxy_type
            proxy_stanza['proxy_rdns'] = proxy_rdns

            if args['proxy_password'][0] != '' or proxy['proxy_username'] != args['proxy_username'][0]:
                stanza = {}
                proxy = {'proxy_username': args['proxy_username']
                         [0], 'proxy_password': args['proxy_password'][0]}
                stanza['seckit_sa_geolocation_proxy'] = proxy

                cred_mgr = cred.CredentialManager(session_key=self.getSessionKey(),
                                                  app=self.appName, splunkd_uri=scc.getMgmtUri())
                try:
                    result = cred_mgr.update(stanza)
                    logger.info("Update result:"+str(result))
                except Exception:
                    logger.error("ERROR in creating cred stanza")
                    logger.error(traceback.format_exc())

            if args['proxy_password'][0] != '' or args['proxy_username'][0] != '':
                proxy_stanza['proxy_username'] = self.encrypted
                proxy_stanza['proxy_password'] = self.encrypted
            else:
                proxy_stanza['proxy_username'] = ''
                proxy_stanza['proxy_password'] = ''

        conf_mgr = conf.ConfManager(splunkd_uri=scc.getMgmtUri(), session_key=self.getSessionKey(),
                                    app_name=self.appName, owner='-')
        success = conf_mgr.update_stanza(
            'seckit_sa_geolocation', 'seckit_sa_geolocation_proxy', proxy_stanza)

        if not success:
            logger.error("ERROR in writing seckit_sa_geolocation conf file.")
        else:
            seckit_sa_geolocation_script_stanza = conf_mgr.get_data_input_stanza(
                'script', script_path, True)
            # restart malware update script when update the proxy settings if the script is enabled, so that the proxy
            # setting will take effect immediately.
            if not utils.is_true(seckit_sa_geolocation_script_stanza.get('disabled', '')):
                conf_mgr.disable_data_input("script", script_path)
                conf_mgr.enable_data_input("script", script_path)

    def _decrypt_username_password(self, confDict):
        try:
            if confDict.get("seckit_sa_geolocation_proxy") is not None:
                account = confDict["seckit_sa_geolocation_proxy"]
                is_encrypted = all(account.get(k, None) == self.encrypted for k in (
                    "proxy_username", "proxy_password"))
                if is_encrypted:
                    cred_mgr = cred.CredentialManager(session_key=self.getSessionKey(),
                                                      app=self.appName, splunkd_uri=scc.getMgmtUri())
                    user_creds = cred_mgr.get_clear_password(
                        "seckit_sa_geolocation_proxy")
                    account["proxy_username"] = user_creds["seckit_sa_geolocation_proxy"]["proxy_username"]
                    account["proxy_password"] = user_creds["seckit_sa_geolocation_proxy"]["proxy_password"]
        except Exception:
            logger.error("decryption error.")
            logger.error(traceback.format_exc())


# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
