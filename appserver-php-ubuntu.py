#!/usr/bin/env fab -f

from fabric.api import run, sudo, task, warn_only
from fabric.contrib import files
from util import apt, service, ConfigFile, sysctl


@task
def server_install():
    # Set kernel options
    with warn_only():
        sysctl('vm.swappiness', 0)

    # Perform updates and installs
    apt.configure()
    apt.upgrade()
    apt.install('software-properties-common', 'ntp', 'uuid', 'zsh', 'screen',
                'tmux', 'vim', 'git', 'subversion',
                'telnet', 'traceroute',
                'curl', 'wget')

    # Performs a quick time sync so all logs are accurate
    with warn_only():
        service.stop('ntp')
        sudo('ntpdate time.nist.gov')
        sudo('ntpdate tick.usno.navy.mil')
        service.start('ntp')
        service.enable('ntp')

    # Install PHP, PHP modules
    apt.install('php5-cli', 'php5-fpm', 'php5-common', 'php5-intl',
                'php5-mcrypt', 'php5-gd', 'php5-curl', 'php5-memcached',
                'php5-xmlrpc', 'php5-mysql', 'php5-pgsql', 'php5-sqlite')

    # Packages yet to be accounted for that we have on the RHEL side:
    # php5-mbstring
    # php5-process
    # php5-pecl-yaml
    # php5-xml
    # php5-soap
    # php5-pdo
    # php5-pecl-apc
    # php5-pecl-memcache
    # php5-redis
    # php5-pecl-mailparse
    # php5-pecl-ssh2
    # php5-pecl-solr

    apt.install('gcc', 'g++', 'make', 'autoconf', 'automake', 'libtool',
                'flex', 'byacc', 'libevent-1.4', 'libevent-2.0', 'php5-dev',
                'libboost-dev', 'libyaml-0-2', 'libyaml-dev',
                'libcurl3', 'libcurl4-openssl-dev',
                'libmemcached6', 'libmemcached-dev',
                'libhiredis0.10', 'libhiredis-dev',
                'openjdk-6-jre', 'openjdk-7-jre',
                'python', 'python-redis', 'python-memcache')

    # Packages yet to be accounted for that we have on the RHEL side:
    # 'mysql-dev'

    # Install MySQL, SQLite, and Nginx
    apt.install('sqlite', 'sqlite3', 'nginx')

    # Update php.ini defaults
    php_inis = ['/etc/php5/fpm/php.ini',
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
    apt.install('mysql-client', 'mysql-server')
    service.enable('mysqld')
    service.start('mysqld')

    # Run the same queries performed by mysql_secure_installation
    queries = [
        "DELETE FROM mysql.user WHERE User='';",
        "DELETE FROM mysql.user WHERE User='root' "
        "AND Host NOT IN ('localhost', '127.0.0.1', '::1');",
        "DROP DATABASE test;",
        "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';",
        "FLUSH PRIVILEGES;",
    ]

    with warn_only():
        for query in queries:
            run('mysql -u root -e "%s"' % query)


@task
def nginx_setup():
    apt.install('nginx')
    service.enable('nginx')
    service.start('nginx')


@task
def memcache_setup():
    apt.install('memcached')
    service.enable('memcached')
    service.start('memcached')


@task
def redis_setup():
    apt.install('redis-server')
    service.enable('redis')
    service.start('redis')
