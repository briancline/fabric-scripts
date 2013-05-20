from __future__ import print_function
from fabric.api import env, run, sudo, task, warn_only, settings
from fabric.colors import green, blue
from util import yum, service, sysctl, file_update, keys

env.user = 'root'
build_user = 'build'
sysfm_repo = 'git://github.com/briancline/sysfm-specs.git'


@task
def push_key():
    keys.push_key()


@task
def bootstrap():
    # Set kernel options
    print(blue('Setting sysctl options...'))
    with warn_only():
        sysctl('vm.swappiness', 0)

    # Basic system configuration
    print(blue('Tweaking configuration...'))
    file_update('/etc/sysconfig/clock', 'ZONE=', 'ZONE="America/Chicago"')
    run('cp -f /usr/share/zoneinfo/America/Chicago /etc/localtime')

    # Update existing packages
    print(blue('Updating installed packages...'))
    yum.update()

    # Install base packages and dev tools
    print(blue('Installing base packages and development tools...'))
    yum.install('yum-utils', 'ntp', 'ntpdate',
                'vim-enhanced', 'git', 'subversion',
                'bind-utils', 'telnet', 'traceroute', 'curl', 'wget',
                'rpm-build', 'rpmdevtools', 'spectool')
    yum.install_group('Development Tools')

    # Perform a quick time sync -- particularly good for VMs
    print(blue('Synchronizing system time...'))
    with warn_only():
        service.stop('ntpd')
        run('ntpdate time.nist.gov')
        run('ntpdate tick.usno.navy.mil')
        service.start('ntpd')
        service.enable('ntpd')

    # Set up build user and their unprivileged environment
    print(blue('Creating %s user and pushing SSH key...' % build_user))
    with warn_only():
        sudo('useradd -m %s' % build_user)
        keys.push_key(user_name=build_user)
        sudo('chown -R %s.%s ~%s/.ssh' % (build_user, build_user, build_user))

    print(blue('Setting up rpmbuild environment...'))
    with settings(user=build_user, warn_only=True):
        run('rpmdev-setuptree')
        run('git clone %s' % sysfm_repo)

    # Huzzah!
    print(green('CentOS build instance ready!'))
