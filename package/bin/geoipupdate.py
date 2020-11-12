import import_declare_test
import sys
import json
import os
import traceback
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log


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
            'seckit_sa_geolocation_input_{}'.format(input_name))

        # Log level configuration
        log_level = get_log_level(session_key, logger)
        logger.setLevel(log_level)

        logger.debug("Modular input invoked.")



        logger.debug("Modular input completed")
if __name__ == '__main__':
    exit_code = GEOIPUPDATE().run(sys.argv)
    sys.exit(exit_code)