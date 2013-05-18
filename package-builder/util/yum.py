from fabric.api import run


def install(*args):
    packages = ' '.join(args)
    run('yum install -y %s' % packages)


def remove(*args):
    packages = ' '.join(args)
    run('yum remove -y %s' % packages)


def update():
    run('yum update -y')


def add_repo(rpm_url):
    run('rpm -Uvh %s' % rpm_url)


def add_epel_repo():
    return add_repo('http://mirror.cogentco.com/pub/linux/epel/6/i386/epel-release-6-8.noarch.rpm')
