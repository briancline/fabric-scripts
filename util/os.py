import re
from fabric.api import run


def parse_version_file(text):
    return {'name': re.findall('(\w+)_version', text)[0],
            'version': text.strip()}


def parse_var_file(text):
    lines = {}

    ## Couldn't find any damned way to do this with a comprehension
    for line in text.strip().split('\n'):
        pair = line.split('=', 1)
        lines[pair[0]] = pair[1]

    return lines


def parse_lsb_file(text):
    lines = parse_var_file(text)
    return {'name': lines['DISTRIB_ID'],
            'version': lines['DISTRIB_RELEASE']}


def parse_os_file(text):
    lines = parse_var_file(text)
    return {'name': lines['ID'],
            'version': lines['VERSION_ID'].strip('"')}


def dist_info():
    file_list = {'/etc/lsb-release': parse_lsb_file,
                 '/etc/os-release': parse_os_file,
                 '/etc/ubuntu_version': parse_version_file,
                 '/etc/debian_version': parse_version_file}

    info = None
    for filename, parser in file_list.iteritems():
        try:
            output = run('cat %s' % filename)
            info = parser(filename, output)
            break
        except Exception:
            pass

    return info


def is_ubuntu():
    return 'ubuntu' == dist_info()['name'].lower()


def is_debian():
    return 'debian' == dist_info()['name'].lower()


def is_redhat():
    return 'rhel' == dist_info()['name'].lower()


def is_centos():
    return 'centos' == dist_info()['name'].lower()
