from __future__ import print_function
from fabric.api import sudo, run
from fabric.contrib import files


class ConfigFile(object):
    def __init__(self, file_name, use_sudo=False):
        self.file_name = file_name
        self.use_sudo = use_sudo
        self.runner = sudo if use_sudo else run

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def sed(self, pattern, replace=None):
        if not replace:
            self.runner("sed -e '%s' -i %s" % (pattern, self.file_name))
        else:
            files.sed(self.file_name, pattern, replace, use_sudo=self.use_sudo)

    def update(self, prefix, text, **kwargs):
        return file_update(self.file_name, prefix, text,
                           use_sudo=self.use_sudo, **kwargs)


def file_update(file_name, prefix, text, use_sudo=False, uncomment=True):
    if uncomment:
        prefix = '^[#;]?\s*%s' % prefix
    else:
        prefix = '^%s' % prefix

    if files.contains(file_name, prefix, escape=False):
        prefix = '%s.*$' % prefix
        files.sed(file_name, prefix, text, use_sudo=use_sudo)
    else:
        files.append(file_name, text, use_sudo=use_sudo)


def sysctl(setting, value=None, do_reload=True):
    seek = '%s\s*=' % setting
    option = '%s=%s' % (setting, value)
    file_update('/etc/sysctl.conf', seek, option, use_sudo=True)

    if do_reload:
        sudo('sysctl -p')
