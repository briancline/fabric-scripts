#!/usr/bin/env fab -f

from fabric.api import run, sudo, task, warn_only
from fabric.contrib import files
from util import yum, service, ConfigFile, file_update, sysctl
from util import keys  # NOQA


REPO_RPMS = {
    'sysfm': 'http://rpm.sys.fm/centos/6/noarch/sysfm-release-6-1.el6.noarch.rpm',
    'remi':  'http://rpms.famillecollet.com/enterprise/remi-release-6.rpm',
    'nginx': 'http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm',
}


@task
def push_key():
    keys.push_key()


@task
def bootstrap():
    keys.push_key()
    server_setup()
    php_setup()
    mysql_setup()
    memcache_setup()
    redis_setup()
    nginx_setup()


@task
def server_setup():
    # Set kernel options
    with warn_only():
        sysctl('vm.swappiness', 0)

    # Basic system configuration
    file_update('/etc/sysconfig/clock', 'ZONE=', 'ZONE="America/Chicago"')
    sudo('cp -f /usr/share/zoneinfo/America/Chicago /etc/localtime')

    # Perform updates and installs
    yum.update()
    yum.install('yum-utils', 'ntp', 'ntpdate', 'uuid', 'zsh', 'screen', 'tmux',
                'vim-enhanced', 'git', 'subversion',
                'bind-utils', 'telnet', 'traceroute',
                'curl', 'wget')

    # Performs a quick time sync so all logs are accurate
    with warn_only():
        service.enable('ntpd')
        service.stop('ntpd')
        sudo('ntpdate time.nist.gov')
        sudo('ntpdate tick.usno.navy.mil')
        service.start('ntpd')

    # Add custom repos for nginx, more up-to-date PHP and MySQL packages,
    # and a few additional PHP modules
    with warn_only():
        yum.add_epel_repo()
        for repo_name, repo_rpm_url in REPO_RPMS.iteritems():
            yum.add_repo_rpm(repo_rpm_url)
            yum.enable_repo(repo_name)


@task
def php_setup():
    # Install PHP, PHP modules, MySQL, SQLite, and Nginx
    yum.install('php-cli', 'php-fpm', 'php-common', 'php-intl', 'php-mbstring',
                'php-mcrypt', 'php-process', 'php-gd',
                'php-pecl-yaml', 'php-xml', 'php-xmlrpc', 'php-soap',
                'php-mysql', 'php-pgsql', 'php-sqlite', 'php-pdo',
                'php-pecl-apc', 'php-pecl-memcache', 'php-redis',
                'php-pecl-mailparse', 'php-pecl-ssh2', 'php-pecl-solr',
                'sqlite', 'sqlite2')

    # Make life easy in the event we need to compile any extensions, or make
    # use of any small backend services
    yum.install('gcc', 'gcc-c++', 'make', 'autoconf', 'automake', 'libtool',
                'flex', 'byacc', 'libevent', 'boost', 'boost-devel',
                'libyaml', 'libyaml-devel', 'libcurl', 'libcurl-devel',
                'curl-devel', 'libmemcached', 'libmemcached-devel', 'hiredis',
                'php-devel', 'mysql-devel',
                'java', 'java-openjdk',
                'python', 'python-redis', 'python-memcached')

    service.enable('php-fpm')

    # Update php.ini defaults
    php_inis = ['/etc/php.ini',
                '/etc/php5/cli/php.ini']
    for ini_file in php_inis:
        if not files.exists(ini_file):
            continue

        with ConfigFile(ini_file, use_sudo=True) as conf:
            conf.update('date.timezone =', 'date.timezone = America/Chicago')
            conf.update('short_open_tag =', 'short_open_tag = On')
            conf.update('expose_php =', 'expose_php = Off')
            conf.update('display_errors =', 'display_errors = Off')
            conf.update('display_startup_errors =',
                        'display_startup_errors = Off')
            conf.update('session.name =', 'session.name = SID')


@task
def mysql_setup():
    # Enable, start, and clean MySQL up
    yum.install('mysql', 'mysql-server')
    service.enable('mysqld')
    service.start('mysqld')

    # Run the same queries performed by mysql_secure_installation
    queries = [
        "DELETE FROM mysql.user WHERE User='';",
        "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');",
        "DROP DATABASE test;",
        "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';",
        "FLUSH PRIVILEGES;",
    ]

    with warn_only():
        for query in queries:
            run('mysql -u root -e "%s"' % query)


@task
def nginx_setup():
    yum.install('nginx')
    service.enable('nginx')
    service.start('nginx')


@task
def memcache_setup():
    yum.install('memcached')
    service.enable('memcached')
    service.start('memcached')


@task
def redis_setup():
    yum.install('redis', 'hiredis')
    service.enable('redis')
    service.start('redis')
