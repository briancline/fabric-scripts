from fabric.api import sudo


def install(*args):
    packages = ' '.join(args)
    sudo('yum install -y %s' % packages)


def remove(*args):
    packages = ' '.join(args)
    sudo('yum remove -y %s' % packages)


def update():
    sudo('yum update -y')


def add_repo_rpm(rpm_url):
    sudo('rpm -Uvh %s' % rpm_url)


def add_epel_repo():
    return add_repo_rpm(
        'http://mirror.cogentco.com/pub/linux/epel/6/i386/'
        'epel-release-6-8.noarch.rpm')
