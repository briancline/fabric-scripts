from fabric.api import run, task, warn_only
from util import yum, service, sysctl, file_update, keys


@task
def push_key():
    keys.push_key()


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
