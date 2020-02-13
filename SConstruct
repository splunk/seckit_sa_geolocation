import os
import subprocess
import sconstool.loader
sconstool.loader.extend_toolpath(transparent=True)


def version_string():
    version = None
    version = subprocess.run('./semtag getcurrent | sed s/v// | sed s/-.*//', shell=True, capture_output=True).stdout.decode("utf-8").replace("\n", '')

    return version

version = version_string()

print("Building version %s" % version)

# Create the base environment with the tool added and some
# suitable (optional) JINJA_ENVIRONMENT_VARS configured.
# JINJA_ENVIRONMENT_VARS does not need to be set here. If required,
# it need only be set on each environment at *some point*.
vars = Variables('build_variables.py')

vars.Add('SPLUNK_BUILD_APP_TITLE', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_NAME', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_VERSION', 'Set for the add-on title', version)
vars.Add('SPLUNK_BUILD_AUTHOR', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_EMAIL', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_COMPANY', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_COMPANY', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_DESCRIPTION', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_LICENSE_NAME', 'Set for the add-on title', 'Untitled add-on')
vars.Add('SPLUNK_BUILD_APP_URI', 'Set for the add-on title', 'Untitled add-on')

env = Environment(tools=['default', 'archives', 'jinja'],
                  variables=vars,
                  JINJA_ENVIRONMENT_VARS={
                      'trim_blocks': True},
                  )

# A simple case

jinja_context = {
    'SPLUNK_BUILD_APP_TITLE': env['SPLUNK_BUILD_APP_TITLE'],
    'SPLUNK_BUILD_APP_NAME': env['SPLUNK_BUILD_APP_NAME'],
    'SPLUNK_BUILD_VERSION': env['SPLUNK_BUILD_VERSION'],
    'SPLUNK_BUILD_AUTHOR': env['SPLUNK_BUILD_AUTHOR'],
    'SPLUNK_BUILD_EMAIL': env['SPLUNK_BUILD_EMAIL'],
    'SPLUNK_BUILD_APP_COMPANY': env['SPLUNK_BUILD_APP_COMPANY'],
    'SPLUNK_BUILD_APP_DESCRIPTION': env['SPLUNK_BUILD_APP_DESCRIPTION'],
    'SPLUNK_BUILD_APP_LICENSE_NAME': env['SPLUNK_BUILD_APP_LICENSE_NAME'],
    'SPLUNK_BUILD_APP_URI': env['SPLUNK_BUILD_APP_URI']
}

jinja_manifest = env.Clone(variables=vars,
                           JINJA_CONTEXT=jinja_context)
jinja_manifest.Depends(target='package/app.manifest', dependency='SConstruct')
jinja_manifest.Depends(target='package/app.manifest', dependency='build_variables.py')

jinja_manifest.Jinja('package/app.manifest',
                     os.path.join('templates', 'app.manifest.jinja'))

jinja_app = env.Clone(variables=vars,
                      JINJA_CONTEXT=jinja_context)
jinja_app.Depends(target='package/default/app.conf', dependency='SConstruct')
jinja_app.Depends(target='package/default/app.conf', dependency='build_variables.py')

jinja_app.Jinja('package/default/app.conf',
                os.path.join('templates', 'app.conf.jinja'))

sources = Glob('package/*', exclude='app.manifest.jinja')

env.TarFile('build/${SPLUNK_BUILD_APP_TITLE}.tar.tgz', sources,
            TARFILEMAPPINGS=[('package', 'SecKit_SA_geolocation'),
                             ])
