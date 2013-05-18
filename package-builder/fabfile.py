from os.path import exists
from fabric.api import run, task, warn_only
from fabric.contrib import files
from fabric.colors import red
from util import yum, service


def file_update(file_name, text, sudo=False, partial=True, escape=True,
                shell=False):
    files.append(file_name, text, use_sudo=sudo,
                 partial=partial, escape=escape, shell=shell)


def sysctl(setting, value=None):
    option = '%s=%s' % (setting, value)
    file_update('/etc/sysctl.conf', option)
    run('sysctl -p')


@task
def push_key():
    if not exists('~/.ssh/id_rsa.pub'):
        print(red('No id_rsa.pub key found.'))
        return

    key = open('~/.ssh/id_rsa.pub').read()
    with warn_only():
        run("mkdir ~/.ssh")
        run("chmod 700 ~/.ssh")
        files.append('~/.ssh/authorized_keys', key)


@task
def server_install():
    # Set kernel options
    with warn_only():
        sysctl('vm.swappiness', 0)

    # Basic system configuration
    file_update('/etc/sysconfig/clock', 'ZONE="America/Chicago"')
    run('cp -f /usr/share/zoneinfo/America/Chicago /etc/localtime')

    # Perform updates and installs
    #apt.configure()
    #apt.install('python-software-properties', 'software-properties-common')

    yum.update()
    yum.remove('cups', 'qt', 'httpd', 'java-1.5.0-gcj')

    with warn_only():
        service.stop('ntpd')
        run('ntpdate time.nist.gov')
        run('ntpdate tick.usno.navy.mil')
        service.start('ntpd')
        service.enable('ntpd')
