from __future__ import print_function
from fabric.api import run, sudo, task, put, warn_only
from util import apt

APT_KEY_URL = 'http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key'
APT_REPO_URL = 'http://pkg.jenkins-ci.org/debian binary/'
APT_LIST_FILE = '/etc/apt/sources.list.d/jenkins.list'

DEADSNAKES_PPA_URL = 'http://ppa.launchpad.net/fkrull/deadsnakes/ubuntu'
DEADSNAKES_LIST_FILE = '/etc/apt/sources.list.d/deadsnakes.list'

PYTHON_VERSIONS = ['2.6', '2.7', '3.1', '3.2', '3.3']


@task
def preflight():
    sudo('mkdir -p ~/.ssh')
    put('~/.ssh/id_rsa.pub', '~/.ssh/authorized_keys', use_sudo=True)
    run('uptime')


@task
def install():
    with warn_only():
        codename = run("grep CODENAME /etc/lsb-release | sed 's|^.*=||'")
        print(codename.strip())

    apt.install('software-properties-common')

    apt.add_key_url(APT_KEY_URL)
    apt.add_repo(APT_REPO_URL, name='jenkins')
    apt.add_repo(DEADSNAKES_PPA_URL)

    apt.update()
    apt.upgrade()

    python_packages = ['python%s' % v for v in PYTHON_VERSIONS]
    apt.install('jenkins')
    apt.install(*python_packages)


@task
def configure():
    pass
