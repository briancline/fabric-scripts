from fabric.api import sudo
from fabric.contrib import files
from patchwork.environment import has_binary


env_vars = 'DEBIAN_FRONTEND=noninteractive'
apt_command = '%s apt-get' % env_vars


def configure():
    sudo('%s dpkg --configure -a' % env_vars)


def add_repo(source, sources_file='/etc/apt/sources.list'):
    if ' ' not in source and has_binary('which add-apt-repository',
                                        runner=sudo):
        sudo('%s add-apt-repository -y %s' % (env_vars, source))
    else:
        files.append(sources_file, source)


def update():
    sudo('%s update -y' % apt_command)


def upgrade():
    sudo('%s upgrade -y' % apt_command)


def dist_upgrade():
    sudo('%s dist-upgrade -y' % apt_command)


def install(*args):
    packages = ' '.join(args)
    sudo('%s install -y %s' % (apt_command, packages))


def remove(*args):
    packages = ' '.join(args)
    sudo('%s remove -y %s' % (apt_command, packages))
