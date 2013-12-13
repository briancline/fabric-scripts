from __future__ import print_function

import sys
import re
import requests

from fabric.api import env, sudo, task
from fabric.colors import blue, green, red
from util import apt
from os.path import basename
from lxml import etree
from distutils.version import StrictVersion

env.use_ssh_config = True

CLOJARS_GROUP = 'riemann'
CLOJARS_ARTIFACT = 'riemann'
ARTIFACT_META_URL = 'https://clojars.org/repo/%s/%s/maven-metadata.xml'
ARTIFACT_XPATH_VER = './/versioning/versions/version'
ARTIFACT_VER_REGEX = r'^\d+\.\d+\.\d+$'
BASE_PACKAGE_URL = 'http://aphyr.com/riemann'


@task
def install():
    latest_ver = latest_version()
    if not latest_ver:
        print(red('Cannot determine latest version. Exiting.'))
        sys.exit(1)

    packages = package_urls(latest_ver)
    deb_url = packages.get('debian')
    file_name = basename(deb_url)

    print(blue('Downloading %s...' % file_name))
    sudo('curl -sO %s' % deb_url)

    print(blue('Installing...'))
    apt.install_from_file(file_name)
    sudo('rm -f %s' % file_name)


def latest_version():
    xml_url = ARTIFACT_META_URL % (CLOJARS_GROUP, CLOJARS_ARTIFACT)
    versions = []
    latest = None

    try:
        print(blue('Determining latest version from clojars...'))
        xml = requests.get(xml_url).text

        xml_root = etree.XML(xml.encode('UTF-8'))
        versions = [node.text
                    for node in xml_root.findall(ARTIFACT_XPATH_VER)
                    if re.match(ARTIFACT_VER_REGEX, node.text)]

        #versions.sort(key=lambda s: map(int, s.split('.')))
        versions.sort(key=StrictVersion)

        latest = versions[-1]
        print(green('Latest version is %s' % latest))
    except Exception as e:
        print(red('Exception: %s' % e))

    return latest


def package_urls(version):
    deb_format = '%s_%s_all.deb' % (CLOJARS_ARTIFACT, version)
    rpm_format = '%s-%s-1.noarch.rpm' % (CLOJARS_ARTIFACT, version)
    tarball_format = '%s-%s.tar.bz2' % (CLOJARS_ARTIFACT, version)

    return {'debian': '%s/%s' % (BASE_PACKAGE_URL, deb_format),
            'redhat': '%s/%s' % (BASE_PACKAGE_URL, rpm_format),
            'other':  '%s/%s' % (BASE_PACKAGE_URL, tarball_format)}
