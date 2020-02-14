
import seckit_sa_geolocation_declare

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    DataInputModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunk_aoblib.rest_migration import ConfigMigrationHandler

util.remove_http_proxy_env_vars()


fields = [

    field.RestField(
        'edition_ids',
        required=True,
        encrypted=False,
        default='GeoLite2-Country GeoLite2-City',
        validator=validator.String(
            min_len=0,
            max_len=8192,
        )
    ),
    field.RestField(
        'global_account',
        required=True,
        encrypted=False,
        default=None,
        validator=None
    ),

    field.RestField(
        'disabled',
        required=False,
        validator=None
    ),
    field.RestField(
        'interval',
        default='10000',
        validator=None
    )

]
model = RestModel(fields, name='main')


endpoint = DataInputModel(
    'geoipupdate',
    model,
)


if __name__ == '__main__':
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
