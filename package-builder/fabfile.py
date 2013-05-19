from os.path import exists, expanduser
from fabric.api import run, task, warn_only
from fabric.contrib import files
from fabric.colors import red
from util import yum, service, sysctl, file_update


@task
def push_key():
    key_path = expanduser('~/.ssh/id_rsa.pub')
    if not exists(key_path):
        print(red('%s not found.' % key_path))
        return

    key = open(key_path).read().strip()
    with warn_only():
        run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        # TODO: $HOME used with append due to a fabric bugfix pending release
        #       Should be available in 1.6.1 or 1.7.0, whichever is next.
        files.append('$HOME/.ssh/authorized_keys', key, partial=True)


@task
def server_install():
    # Set kernel options
    with warn_only():
        sysctl('vm.swappiness', 0)

    # Basic system configuration
    file_update('/etc/sysconfig/clock', 'ZONE=', 'ZONE="America/Chicago"')
    run('cp -f /usr/share/zoneinfo/America/Chicago /etc/localtime')

    yum.update()
    yum.install('ntp')

    with warn_only():
        service.stop('ntpd')
        run('ntpdate time.nist.gov')
        run('ntpdate tick.usno.navy.mil')
        service.start('ntpd')
        service.enable('ntpd')
