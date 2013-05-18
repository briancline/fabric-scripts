from fabric.api import run


def configure():
    run('dpkg --configure -a')


def add_repo(url):
    run('add-apt-repository -y %s' % url)


def update():
    run('apt-get update -y')


def upgrade():
    run('apt-get upgrade -y')


def dist_upgrade():
    run('apt-get dist-upgrade -y')


def install(*kwargs):
    packages = ' '.join(*kwargs)
    run('apt-get install -y %s' % packages)


def remove(*kwargs):
    packages = ' '.join(*kwargs)
    run('apt-get remove -y %s' % packages)
