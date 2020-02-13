from builtins import str
import splunktalib.common.xml_dom_parser as xdp
from splunktalib.conf_manager.request import _content_request

CONF_ENDPOINT = "%s/servicesNS/%s/%s/configs/conf-%s"


def _conf_endpoint_ns(uri, owner, app, conf_name):
    return CONF_ENDPOINT % (uri, owner, app, conf_name)


def reload_conf_ns(splunkd_uri, session_key, app_name, conf_name):
    """
    :param splunkd_uri: splunkd uri, e.g. https://127.0.0.1:8089
    :param session_key: splunkd session key
    :param conf_names: a list of the name of the conf file, e.g. ['props']
    :param app_name: the app's name, e.g. 'Splunk_TA_aws'
    :return: None
    """

    uri = _conf_endpoint_ns(splunkd_uri, 'nobody', app_name, conf_name)
    uri += '/_reload'
    msg = "Failed to reload conf in app=%s: %s" % (app_name, conf_name)
    content = _content_request(uri, session_key, "GET", None, msg)
    if content is None:
        return False
    return True


def create_stanza_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                     stanza, key_values=None):
    """
    :param splunkd_uri: splunkd uri, e.g. https://127.0.0.1:8089
    :param session_key: splunkd session key
    :param owner: the owner (ACL user), e.g. '-', 'nobody'
    :param app_name: the app's name, e.g. 'Splunk_TA_aws'
    :param conf_name: the name of the conf file, e.g. 'props'
    :param stanza: stanza name, e.g. 'aws:cloudtrail'
    :param key_values: the key-value dict of the stanza
    :return: True on success
    """
    if key_values is None:
        key_values = {}

    uri = _conf_endpoint_ns(splunkd_uri, owner, app_name, conf_name)
    msg = "Failed to create stanza=%s in conf=%s" % (stanza, conf_name)
    payload = {"name": stanza}
    for key in key_values:
        if key != 'name':
            payload[key] = str(key_values[key])

    res = _content_request(uri, session_key, "POST", payload, msg)
    return res is not None


def get_conf_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                stanza=None):
    """
    :param splunkd_uri: splunkd uri, e.g. https://127.0.0.1:8089
    :param session_key: splunkd session key
    :param owner: the owner (ACL user), e.g. '-', 'nobody'
    :param app_name: the app's name, e.g. 'Splunk_TA_aws'
    :param conf_name: the name of the conf file, e.g. 'props'
    :param stanza: stanza name, e.g. 'aws:cloudtrail'
    :return: the key-value dict of the stanza, or a list of stanzas in
             the conf file, including metadata
    """
    uri = _conf_endpoint_ns(splunkd_uri, owner, app_name, conf_name)

    if stanza:
        uri += '/' + stanza.replace('/', '%2F')

    msg = "Failed to get conf={0}, stanza={1}".format(conf_name, stanza)
    content = _content_request(uri, session_key, "GET", None, msg)
    if content is not None:
        result = xdp.parse_conf_xml_dom(content)
        if stanza:
            result = result[0]
        return result
    return None


def update_stanza_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                     stanza, key_values):
    """
    :param splunkd_uri: splunkd uri, e.g. https://127.0.0.1:8089
    :param session_key: splunkd session key
    :param owner: the owner (ACL user), e.g. '-', 'nobody'
    :param app_name: the app's name, e.g. 'Splunk_TA_aws'
    :param conf_name: the name of the conf file, e.g. 'props'
    :param stanza: stanza name, e.g. 'aws:cloudtrail'
    :param key_values: the key-value dict of the stanza
    :return: True on success
    """
    uri = _conf_endpoint_ns(splunkd_uri, owner, app_name, conf_name)
    uri += '/' + stanza.replace('/', '%2F')
    msg = "Failed to update stanza=%s in conf=%s" % (stanza, conf_name)

    res = _content_request(uri, session_key, "POST", key_values, msg)
    return res is not None


def delete_stanza_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                     stanza):
    """
    :param splunkd_uri: splunkd uri, e.g. https://127.0.0.1:8089
    :param session_key: splunkd session key
    :param owner: the owner (ACL user), e.g. '-', 'nobody'
    :param app_name: the app's name, e.g. 'Splunk_TA_aws'
    :param conf_name: the name of the conf file, e.g. 'props'
    :param stanza: stanza name, e.g. 'aws:cloudtrail'
    :return: True on success
    """
    uri = _conf_endpoint_ns(splunkd_uri, owner, app_name, conf_name)
    uri += '/' + stanza.replace('/', '%2F')
    msg = "Failed to delete stanza=%s in conf=%s" % (stanza, conf_name)

    res = _content_request(uri, session_key, "DELETE", None, msg)
    return res is not None


def check_stanza_exist_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                          stanza):
    result = get_conf_ns(splunkd_uri, session_key, owner, app_name, conf_name,
                         stanza)
    return result is not None
