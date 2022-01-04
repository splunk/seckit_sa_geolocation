# SPDX-FileCopyrightText: 2020 Splunk Inc (Ryan Faircloth) <rfaircloth@splunk.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
This controller does the update
"""
import logging
import os
import re
import subprocess
import sys
import tempfile
from os.path import dirname

from seckit_helpers import rest_handler
from splunk.clilib.bundle_paths import make_splunkhome_path

ta_name = "SecKit_SA_geolocation"
pattern = re.compile(r"[\\/]etc[\\/]apps[\\/][^\\/]+[\\/]bin[\\/]?$")
new_paths = [path for path in sys.path if not pattern.search(path) or ta_name in path]
new_paths.append(os.path.join(dirname(dirname(__file__)), "lib"))
new_paths.insert(0, os.path.sep.join([os.path.dirname(__file__), ta_name]))
sys.path = new_paths


def setup_logger(level):
    """
    Setup a logger for the REST handler
    """

    logger = logging.getLogger(
        "splunk.appserver.SecKit_SA_geolocation_rh_updater.handler"
    )
    logger.propagate = (
        False  # Prevent the log messages from being duplicated in the python.log file
    )
    logger.setLevel(level)

    log_file_path = make_splunkhome_path(
        ["var", "log", "splunk", "SecKit_SA_geolocation_rh_updater.log"]
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=25000000, backupCount=5
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s pid=%(process)d tid=%(threadName)s "
        "file=%(filename)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger(logging.INFO)


class GeoipUpdateHandler(rest_handler.RESTHandler):
    """
    This is a REST handler that supports backing up lookup files.
    This is broken out as a separate handler so that this handler can be replayed on other search
    heads via the allowRestReplay setting in restmap.conf.
    """

    def __init__(self, command_line, command_arg):
        super().__init__(command_line, command_arg, logger)

    def post_update(self, request_info, id, token, db, proxy_settings=None, **kwargs):
        logger.info("Asked to update")
        # in_string = "sdfsd"
        logger.info(f"Asked to update {request_info}")
        logger.info(f"Asked to update id={id} token={token} db={db}")
        # payload = json.loads(request["payload"])

        try:
            proxy_settings = {}
            logger.info("Trying to update")
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".conf", prefix="GeoIP"
            ) as file:
                file.write("\nAccountID " + id)
                file.write("\nLicenseKey " + token)
                file.write("\nEditionIDs " + db)

                if proxy_settings == {}:
                    logger.debug("no proxy")
                else:
                    file.write(
                        "\nProxy "
                        + proxy_settings["proxy_url"]
                        + ":"
                        + proxy_settings["proxy_port"]
                    )
                    if not proxy_settings["proxy_username"] is None:
                        file.write(
                            "\nProxyUserPassword "
                            + proxy_settings["proxy_username"]
                            + ":"
                            + proxy_settings["proxy_password"]
                        )

                file.flush()
                guargs = str(
                    os.path.expandvars(
                        "-v -d $SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/ -f "
                        + file.name
                    )
                )

                try:
                    subprocess.check_output(
                        [
                            "$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/bin/geoipupdate/linux_amd64/geoipupdate "
                            + guargs
                        ],
                        shell=True,  # nosemgrep:
                        stderr=subprocess.STDOUT,
                    )
                except subprocess.CalledProcessError as e:
                    logger.exception(e)
                    logger.error("command args:\n")
                    logger.error(e.cmd)
                    logger.error("output:\n")
                    logger.error(e.output.decode("utf-8"))
                    sys.exit(1)

                mmdb_dir = os.path.expandvars(
                    "$SPLUNK_HOME/etc/apps/SecKit_SA_geolocation/data/"
                )
                files = os.listdir(mmdb_dir)
                for name in files:
                    if name.endswith(".mmdb"):
                        inode = os.stat(os.path.join(mmdb_dir, name))
                        logger.info(
                            "mmdb="
                            + name
                            + " size="
                            + str(inode.st_size)
                            + " mtime="
                            + str(inode.st_mtime)
                        )

            # Everything worked, return accordingly
            return {
                "payload": "done",  # Payload of the request.
                "status": 200,  # HTTP status code
            }

        except:  # noqa

            logger.exception(
                "Exception generated when attempting to backup a lookup file"
            )
            return {
                "payload": "Failed",  # Payload of the request.
                "status": 500,  # HTTP status code
            }
