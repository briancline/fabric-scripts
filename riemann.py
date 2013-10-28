from __future__ import print_function
from fabric.api import env, sudo, task
from util import apt
from os.path import basename

env.hosts = ['riemann']
env.user = 'root'
env.use_ssh_config = True

deb_url = 'http://aphyr.com/riemann/riemann_0.2.2_all.deb'
rpm_url = 'http://aphyr.com/riemann/riemann-0.2.2-1.noarch.rpm'
tar_url = 'http://aphyr.com/riemann/riemann-0.2.2.tar.bz2'


@task
def install():
    file_name = basename(deb_url)
    sudo('curl -O %s' % deb_url)
    apt.install_from_file(file_name)
    sudo('rm -f %s' % file_name)
