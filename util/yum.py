from fabric.api import sudo, settings, hide
from patchwork.environment import has_binary


def install(*args):
    packages = ' '.join(args)
    sudo('yum install -y %s' % packages)


def install_group(*args):
    for group in args:
        sudo('yum groupinstall -y "%s"' % group)


def remove(*args):
    packages = ' '.join(args)
    sudo('yum remove -y %s' % packages)


def update():
    sudo('yum update -y')


def add_repo_rpm(rpm_url):
    sudo('rpm --quiet -Uvh %s' % rpm_url)


def add_epel_repo():
    return add_repo_rpm(
        'http://mirror.cogentco.com/pub/linux/epel/6/i386/'
        'epel-release-6-8.noarch.rpm')


def enable_repo(repo_name):
    if has_binary('yum-config-manager'):
        with settings(hide('output')):
            sudo('yum-config-manager --enable %s' % repo_name)
    else:
        # TODO: somebody call the hack police (or install yum-utils, you putz)
        #
        # Assumes first "enabled=" entry in a yum.repos.d file is the main
        # source, and not a debug/test/etc package source, and that it appears
        # in the first 8 lines.
        sudo("sed -i '1,8s/enabled=./enabled=1/' /etc/yum.repos.d/%s.repo" %
             repo_name)


def disable_repo(repo_name):
    if has_binary('yum-config-manager'):
        with settings(hide('output')):
            sudo('yum-config-manager --disable %s' % repo_name)
    else:
        # TODO: same note as above in enable_repo
        sudo("sed -i '1,8s/enabled=./enabled=0/' /etc/yum.repos.d/%s.repo" %
             repo_name)
