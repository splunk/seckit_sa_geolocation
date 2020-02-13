import splunktalib.rest as rest
from splunktalib.common import log

_LOGGER = log.Logs().get_logger("ta_util_conf_manager")


def _content_request(uri, session_key, method, payload, err_msg):
    resp, content = rest.splunkd_request(uri, session_key, method,
                                         data=payload, retry=3)
    if resp is None and content is None:
        return None

    if resp.status in (200, 201):
        return content
    else:
        _LOGGER.error("%s, reason=%s", err_msg, resp.reason)
    return None
