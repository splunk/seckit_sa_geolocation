import import_declare_test
import splunk.admin as admin
import splunk.clilib.cli_common as scc
import splunktalib.common.util as utils
from splunktalib.conf_manager import conf_manager as conf
from splunktalib.common import log
import logging

utils.remove_http_proxy_env_vars()
logger = log.Logs().get_logger('seckit_sa_geolocation', level=logging.DEBUG)

"""
Copyright (C) 2005 - 2015 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values 
      corresponds to handleractions = edit in restmap.conf
"""


class ConfigApp(admin.MConfigHandler):
    """
    Set up supported arguments
    """

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['script_enabled', 'interval']:
                self.supportedArgs.addOptArg(arg)

    """
    Read the initial values of the parameters from the custom file
      myappsetup.conf, and write them to the setup screen.

    If the app has never been set up,
      uses .../<appname>/default/myappsetup.conf.

    If app has been set up, looks at
      .../local/myappsetup.conf first, then looks at
    .../default/myappsetup.conf only if there is no value for a field in
      .../local/myappsetup.conf

    For boolean fields, may need to switch the true/false setting.

    For text fields, if the conf file says None, set to the empty string.
    """

    def handleList(self, confInfo):
        confDict = self.readConf("inputs")
        if None != confDict:
            for stanza, settings in list(confDict.items()):
                if stanza in ['script://$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoip_update.py']:
                    for key, val in list(settings.items()):
                        if key == "disabled":
                            if val == '0':
                                val = '1'
                            else:
                                val = '0'
                            confInfo['seckit_sa_geolocation_script'].append(
                                "script_enabled", val)
                        else:
                            confInfo['seckit_sa_geolocation_script'].append(
                                key, val)

    """
    After user clicks Save on setup screen, take updated parameters,
    normalize them, and save them somewhere
    """

    def handleEdit(self, confInfo):
        args = self.callerArgs.data
        # Validate interval
        interval = args['interval'][0]
        if not interval.isdigit():
            raise admin.ArgValidationException("Interval should be digit")

        conf_mgr = conf.ConfManager(splunkd_uri=scc.getMgmtUri(), session_key=self.getSessionKey(),
                                    app_name=self.appName, owner='-')
        script_enabled = int(args['script_enabled'][0])
        account = args['account'][0]

        stanza = {"interval": interval}
        success = conf_mgr.update_data_input("script",
                                             "$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoip_update.py",
                                             stanza)
        if not success:
            logger.error("ERROR in updating script input")

        if script_enabled == 1:
            conf_mgr.enable_data_input("script",
                                       "$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoip_update.py")
        else:
            conf_mgr.disable_data_input("script",
                                        "$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoip_update.py")


# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
