from __future__ import print_function
from fabric.api import run


class ConfigFile(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def sed(self, pattern):
        run("sed -e '%s' -i %s" % (pattern, self.file_name))
