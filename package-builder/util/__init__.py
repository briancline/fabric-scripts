from __future__ import print_function
from fabric.api import run
from fabric.contrib import files


class ConfigFile(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def sed(self, pattern):
        run("sed -e '%s' -i %s" % (pattern, self.file_name))


def file_update(file_name, prefix, text, use_sudo=False):
    prefix = '^%s' % prefix
    if files.contains(file_name, prefix, escape=False):
        prefix = '%s.*$' % prefix
        files.sed(file_name, prefix, text)
    else:
        files.append(file_name, text, use_sudo=use_sudo)


def sysctl(setting, value=None, reload=True):
    seek = '%s\s*=' % setting
    option = '%s=%s' % (setting, value)
    file_update('/etc/sysctl.conf', seek, option, use_sudo=True)

    if reload:
        run('sysctl -p')
