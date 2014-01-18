#!/usr/bin/env fab -f

from __future__ import print_function
from fabric.api import run, sudo, task, warn_only, env
from fabric.context_managers import cd
from fabric.contrib import files
from util import apt, sysctl
from util import keys

DOTFILES_REPO = 'https://github.com/briancline/dotfiles.git'

env.use_ssh_config = True


@task
def info():
    run('uptime')
    run('uname -a')
    run('lsb_release -i -d -r -c')


@task
def push_key(user=None, keyfile=None):
    keys.push_key(keyfile, user)


@task
def adduser(user='bc', keyfile=None, shell='/bin/bash'):
    sudo("useradd -U -p '*' -m -s %s %s" % (shell, user))
    sudo('usermod -a -G chsh %s' % user)
    keys.push_key(keyfile, user)
    sudo("echo '%s ALL=(ALL:ALL) NOPASSWD:ALL' > /etc/sudoers.d/%s.sudo" %
         (user, user))


@task
def setup_env(user='bc'):
    apt.install('zsh', 'git')
    run('rm -rf .env')
    run('git clone %s .env' % DOTFILES_REPO)
    with cd('.env'):
        run('./install.sh')


@task
def server_prep():
    with warn_only():
        sudo('groupadd chsh')

    if not files.contains('/etc/pam.d/chsh', 'trust group=chsh'):
        ## Terrible way to prepend to a file. DERP and MUR, accordingly.
        sudo("sed -e '1i# This allows users to change their own shell' "
             "    -e '1i# without being prompted for a password' "
             "    -e '1iauth   sufficient   pam_wheel.so trust group=chsh\\n' "
             "    -ri /etc/pam.d/chsh")

    with warn_only():
        sysctl('vm.swappiness', 0)
