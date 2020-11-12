
# encoding = utf-8

import os
import sys
import time
import datetime
import tempfile
import subprocess

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.


# def use_single_instance_mode():
#    return True


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # edition_ids = definition.parameters.get('edition_ids', None)
    # global_account = definition.parameters.get('global_account', None)
    pass


def collect_events(helper, ew):
 # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()

    opt_edition_ids = str(helper.get_arg('edition_ids'))

    opt_license = helper.get_arg('global_account')

    account = str(opt_license["username"])
    license = str(opt_license["password"])
    helper.log_info("Updating for Account " + account)


#            file = tempfile.NamedTemporaryFile(mode='w',suffix=".conf", prefix="GeoIP")
    with tempfile.NamedTemporaryFile(mode='w', suffix=".conf", prefix="GeoIP") as file:
        file.write("\nAccountID " + account)
        file.write("\nLicenseKey " + license)
        file.write("\nEditionIDs " + opt_edition_ids + "\n")

        if proxy_settings == {}:
            helper.log_info("no proxy")
        else:
            file.write(
                "\nProxy " + proxy_settings["proxy_url"] + ":" + proxy_settings["proxy_port"])
            if not proxy_settings["proxy_username"] is None:
                file.write(
                    "\nProxyUserPassword " + proxy_settings["proxy_username"] + ":" + proxy_settings["proxy_password"])

        file.flush()
        guargs = str(os.path.expandvars(
            "-v -d $SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/ -f " + file.name))
        helper.log_info(guargs)

        result = subprocess.check_output(
            ["$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoipupdate/linux_amd64/geoipupdate " + guargs], shell=True)
        helper.log_info('result ' + str(result))

        mmdb_dir = os.path.expandvars(
            '$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/')
        files = os.listdir(mmdb_dir)
        for name in files:
            if name.endswith('.mmdb'):
                inode = os.stat(os.path.join(mmdb_dir, name))
                helper.log_info(
                    'mmdb=' + name + ' size=' +
                    str(inode.st_size) + ' mtime=' + str(inode.st_mtime)
                )

    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_edition_ids = helper.get_arg('edition_ids')
    opt_global_account = helper.get_arg('global_account')
    # In single instance mode, to get arguments of a particular input, use
    opt_edition_ids = helper.get_arg('edition_ids', stanza_name)
    opt_global_account = helper.get_arg('global_account', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_userdefined_global_var = helper.get_global_setting("userdefined_global_var")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''
