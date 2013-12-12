from fabric.api import sudo
from fabric.contrib import files
from patchwork.environment import has_binary


env_vars = 'DEBIAN_FRONTEND=noninteractive'
apt_command = '%s apt-get' % env_vars
apt_args = '-q -y'


def configure():
    sudo('%s dpkg --configure -a' % env_vars)


def install_from_file(file_name):
    sudo('%s dpkg -i %s' % (env_vars, file_name))


def add_repo(source, sources_file='/etc/apt/sources.list'):
    if ' ' not in source and has_binary('which add-apt-repository',
                                        runner=sudo):
        sudo('%s add-apt-repository -y %s' % (env_vars, source))
    else:
        files.append(sources_file, source)


def update():
    sudo('%s update %s' % (apt_command, apt_args))


def upgrade():
    sudo('%s upgrade %s' % (apt_command, apt_args))


def dist_upgrade():
    sudo('%s dist-upgrade %s' % (apt_command, apt_args))


def install(*args):
    packages = ' '.join(args)
    sudo('%s install %s %s' % (apt_command, apt_args, packages))


def remove(*args):
    packages = ' '.join(args)
    sudo('%s remove %s %s' % (apt_command, apt_args, packages))
