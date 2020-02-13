"""
Handles credentials related stuff
"""

from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import xml.dom.minidom as xdm
import urllib.parse

import splunktalib.common.xml_dom_parser as xdp
import splunktalib.rest as rest
from splunktalib.common import log


_LOGGER = log.Logs().get_logger("ta_util")


class CredException(Exception):
    pass


class CredentialManager(object):
    """
    Credential related interfaces
    """

    _log_template = "Failed to %s user credential for %s, app=%s"

    def __init__(self, session_key=None, username=None,
                 password=None, app="-", owner="-",
                 realm=None, splunkd_uri="https://localhost:8089"):
        self._app = app
        self._splunkd_uri = splunkd_uri
        self._owner = owner
        self._sep = "``splunk_cred_sep``"

        if realm:
            self._realm = realm
        else:
            self._realm = app

        if session_key:
            self._session_key = session_key
        elif username and password:
            self._session_key = self.get_session_key(username,
                                                     password, splunkd_uri)
        else:
            msg = "Need session_key or one of username & password."
            _LOGGER.error(msg)
            raise CredException(msg)

    @staticmethod
    def get_session_key(username, password,
                        splunkd_uri="https://localhost:8089"):
        """
        Get session key by using login username and passwrod
        @return: session_key if successful, None if failed
        """

        eid = "".join((splunkd_uri, "/services/auth/login"))
        postargs = {
            "username": username,
            "password": password,
        }

        response, content = rest.splunkd_request(
            eid, None, method="POST", data=postargs)

        if response is None and content is None:
            return None

        xml_obj = xdm.parseString(content)
        session_nodes = xml_obj.getElementsByTagName("sessionKey")
        if not session_nodes:
            raise CredException("Invalid username or password.")
        session_key = session_nodes[0].firstChild.nodeValue
        if not session_key:
            raise CredException("Get session key failed.")
        return session_key

    def update(self, stanza):
        """
        Update or Create credentials based on the stanza
        @return: True if successful, False if failure
        """
        success = True
        for name, encr_dict in list(stanza.items()):
            encrypts = []
            for key, val in list(encr_dict.items()):
                encrypts.append(key)
                encrypts.append(val)
            success = self._update(name, self._sep.join(encrypts))
            if not success:
                _LOGGER.error("Failed to encrypt name %s", name)
                success = False
        return success

    def _update(self, name, str_to_encrypt):
        """
        Update the string for the name.
        @return: True if successful, False if failure
        """

        self.delete(name)
        return self._create(name, str_to_encrypt)

    def _create(self, name, str_to_encrypt):
        """
        Create a new stored credential.
        @return: True if successful, False if failure
        """

        payload = {
            "name": name,
            "password": str_to_encrypt,
            "realm": self._realm,
        }

        endpoint = self._get_endpoint(name)
        resp, content = rest.splunkd_request(endpoint, self._session_key,
                                             method="POST", data=payload)
        if resp and resp.status in (200, 201):
            return True
        return False

    def delete(self, name):
        """
        Delete the encrypted entry
        @return: True for success, False for failure
        """

        endpoint = self._get_endpoint(name)
        response, content = rest.splunkd_request(
            endpoint, self._session_key, method="DELETE")
        if response and response.status in (200, 201):
            return True
        return False

    def get_all_passwords(self):
        """
        @return: a list of dict when successful, None when failed.
        the dict at least contains
        {
            "realm": xxx,
            "username": yyy,
            "clear_password": zzz,
        }
        """

        endpoint = "{}/services/storage/passwords".format(self._splunkd_uri)
        response, content = rest.splunkd_request(
            endpoint, self._session_key, method="GET")
        if response and response.status in (200, 201) and content:
            return xdp.parse_conf_xml_dom(content)

    def get_clear_password(self, name=None):
        """
        @return: clear password(s)
        """

        return self._get_credentials("clear_password", name)

    def get_encrypted_password(self, name=None):
        """
        @return: encyrpted password(s)
        """

        return self._get_credentials("encr_password", name)

    def _get_credentials(self, prop, name=None):
        """
        @return: clear or encrypted password for specified realm, user
        """

        endpoint = self._get_endpoint(name)
        response, content = rest.splunkd_request(
            endpoint, self._session_key, method="GET")

        results = {}
        if response and response.status in (200, 201) and content:
            passwords = xdp.parse_conf_xml_dom(content)
            for password in passwords:
                if password.get("realm") == self._realm:
                    values = password[prop].split(self._sep)
                    if len(values) % 2 == 1:
                        continue
                    result = {values[i]: values[i + 1]
                              for i in range(0, len(values), 2)}
                    results[password.get("username")] = result

        return results

    @staticmethod
    def _build_name(realm, name):
        return urllib.parse.quote(
            "".join((CredentialManager._escape_string(realm), ":",
                     CredentialManager._escape_string(name), ":")))

    @staticmethod
    def _escape_string(string_to_escape):
        """
        Splunk secure credential storage actually requires a custom style of
        escaped string where all the :'s are escaped by a single \.
        But don't escape the control : in the stanza name.
        """

        return string_to_escape.replace(":", "\\:").replace("/", "%2F")

    def _get_endpoint(self, name=None):
        if name:
            realm_user = self._build_name(self._realm, name)
            rest_endpoint = "{}/servicesNS/{}/{}/storage/passwords/{}".format(
                self._splunkd_uri, self._owner, self._app, realm_user)
        else:
            rest_endpoint = "{}/servicesNS/{}/{}/storage/passwords".format(
                self._splunkd_uri, self._owner, self._app)
        return rest_endpoint
