from fabric.api import sudo, settings
from fabric.contrib import files
from patchwork.environment import has_binary


APT_ENV_VARS = 'DEBIAN_FRONTEND=noninteractive'
APT_COMMAND = '%s apt-get' % APT_ENV_VARS
APT_ARGS = '-q -y'


def configure():
    sudo('%s dpkg --configure -a' % APT_ENV_VARS)


def install_from_file(file_name):
    sudo('%s dpkg -i %s' % (APT_ENV_VARS, file_name))


def add_key_url(url):
    sudo('curl -sS %s | apt-key add -' % url)


def add_repo(url, name=None, source_packages=False, remove=False):
    repo_type = 'deb' if not source_packages else 'deb-src'
    sources_file = '/etc/apt/sources.list'

    if not name:
        sources_file = '/etc/apt/sources.list.d/%s.list' % name

    if ' ' not in url and has_binary('which add-apt-repository', runner=sudo):
        add_args = ' '.join(['-s' if source_packages else '',
                             '-r' if remove else ''])
        sudo('%s add-apt-repository -y %s "%s"' % (APT_ENV_VARS,
                                                   add_args, url))
    elif not remove:
        sources_line = '%s %s' % (repo_type, url)
        files.append(sources_file, sources_line)

    if remove:
        sources_line = '%s %s' % (repo_type, url)
        with settings(warn_only=True):
            grep_result = sudo("grep -rn '%s' "
                               "/etc/apt/sources.list "
                               "/etc/apt/sources.list.d/*.list"
                               % sources_line)

            if grep_result.return_code == 0:
                for grep_output_line in grep_result.split('\n'):
                    grep_params = grep_output_line.split(':', 3)[0:2]
                    file_name = grep_params[0]
                    line_num = grep_params[1]
                    sudo("sed -i '%sd' %s" % (line_num, file_name))


def remove_repo(url, name=None, source_packages=False):
    return add_repo(url, name=name, source_packages=source_packages,
                    remove=True)


def update():
    sudo('%s update %s' % (APT_COMMAND, APT_ARGS))


def upgrade():
    sudo('%s upgrade %s' % (APT_COMMAND, APT_ARGS))


def dist_upgrade():
    sudo('%s dist-upgrade %s' % (APT_COMMAND, APT_ARGS))


def install(*args):
    packages = ' '.join(args)
    sudo('%s install %s %s' % (APT_COMMAND, APT_ARGS, packages))


def remove(*args):
    packages = ' '.join(args)
    sudo('%s remove %s %s' % (APT_COMMAND, APT_ARGS, packages))
