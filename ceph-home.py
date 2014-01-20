#!/usr/bin/env fab -f
"""
Manages Ceph cluster in ADS1 (Addison)
- Shows uptime
- Creates ceph user account, sets up SSH key auth, provides sudo
- Shows total cluster capacity
- Shows ideal PG size based on cluster characteristics
- TODO: Create a pool
"""

from __future__ import print_function
import fabric
from fabric.api import env, task, roles, parallel, run
from fabric.colors import green, blue  # red, yellow,
from fabric.contrib.files import append
from os.path import expanduser
#from pprint import pprint


REPLICA_COUNT = 2
OSD_COUNT = 4

DC = 'ads1'
CLUSTERS = {
    'ads1': {
        'name': 'Addison 01',
        'loc_country': 'US',
        'loc_entity': 'TX',
        'loc_city': 'Addison',

        'logical_path': '/US/TX/Addison/ads1',
        'crush_path': '/root/ads1',
        'replica_min': 1,
        'replica_max': 2,

        'hosts': {
            'heap01': {
                'logical_path': 'sr01/row01/rack01/slot01/heap01',
                'crush_path': '/ads1/sr01/row01/rack01/heap01',

                'roles': ['mds', 'mon', 'osd'],
                'tags': ['ceph',
                         'ipmi',
                         'fs.os.xfs',
                         'fs.data.xfs'],

                'fqdn': 'heap01.ads1.sysnw.net',
                'os': ['Ubuntu', 'Ubuntu 13.10',
                       '13.10', 'saucy'],
                'kernel': ['Linux', '3.11.0-14-generic',
                           '#21-Ubuntu SMP Tue Nov 12 17:04:55 UTC 2013',
                           'x86_64', 'x86_64', 'x86_64'],

                'hotswap_os': 1,
                'hotswap_slots': 4,
                'hotswap_free': 0,
                'hotswap_sizes_gb': [932, 2795, 2795, 2795],
                'internal_sizes_gb': [],
            },
            'heap02': {
                'logical_path': 'sr01/row01/rack01/slot02/heap02',
                'crush_path': '/ads1/sr01/row01/rack01/heap02',

                'roles': ['osd'],
                'tags': ['ceph',
                         'ipmi',
                         'fs.os.xfs',
                         'fs.data.xfs',
                         'migrate.os'],

                'fqdn': 'heap02.ads1.sysnw.net',
                'os': ['Ubuntu', 'Ubuntu 13.10',
                       '13.10', 'saucy'],
                'kernel': ['Linux', '3.11.0-14-generic',
                           '#21-Ubuntu SMP Tue Nov 12 17:04:55 UTC 2013',
                           'x86_64', 'x86_64', 'x86_64'],

                'hotswap_os': 1,
                'hotswap_slots': 4,
                'hotswap_free': 1,
                'hotswap_sizes_gb': [149, 2795, 1863, 2795],
                'internal_sizes_gb': [],
            },
            'file01': {
                'logical_path': 'sr01/row01/rack01/slot03/file01',
                'crush_path': '/ads1/sr01/row01/rack01/file01',

                'roles': ['consumer', 'rbd'],
                'tags': ['lvm',
                         'ipmi',
                         'fs.os.ext4',
                         'migrate.os'],

                'fqdn': 'file01.ads1.sysnw.net',
                'os': ['CentOS', 'CentOS release 6.4 (Final)',
                       '6.4', 'Final'],
                'kernel': ['Linux', '2.6.32-358.18.1.el6.x86_64',
                           '#1 SMP Wed Aug 28 17:19:38 UTC 2013',
                           'x86_64', 'x86_64', 'x86_64'],

                'hotswap_os': 0,
                'hotswap_slots': 0,
                'hotswap_free': 0,
                'hotswap_sizes_gb': [],
                'internal_sizes_gb': [234],
            },
            'file02': {
                'logical_path': 'sr01/row01/rack01/slot04/file02',
                'crush_path': '/ads1/sr01/row01/rack01/file02',

                'roles': ['deploy', 'consumer', 'rbd'],
                'tags': ['lvm',
                         'ipmi',
                         'fs.os.lvm-single.ext3'
                         'fs.data.lvm-split.ext4',
                         'migrate.data'],

                'fqdn': 'file02.ads1.sysnw.net',
                'os': ['Debian', 'Debian GNU/Linux 7.2 (wheezy)',
                       '7.2', 'wheezy'],
                'kernel': ['Linux', '3.2.0-4-amd64',
                           '#1 SMP Debian 3.2.51-1',
                           'x86_64', 'unknown', 'unknown'],

                'hotswap_os': 1,
                'hotswap_slots': 4,
                'hotswap_free': 1,
                'hotswap_sizes_gb': [153, None, 932, 932],
                'internal_sizes_gb': [],
            },
            'hal': {
                ## hal is not used for ceph, but possible future monitor node
                'logical_path': 'sr02/row01/rack01/slot01/hal',
                'crush_path': '/ads1/sr02/row01/rack01/hal',

                'roles': ['consumer'],
                'tags': ['lvm',
                         'fs.os.lvm-single.ext3'
                         'fs.data.lvm-split.ext4',
                         'migrate.data'],

                'fqdn': 'file02.ads1.sysnw.net',
                'os': ['CentOS', 'CentOS release 6.4 (Final)',
                       '6.4', 'Final'],
                'kernel': ['Linux', '2.6.32-358.6.1.el6.x86_64',
                           '#1 SMP Tue Apr 23 19:29:00 UTC 2013',
                           'x86_64', 'x86_64', 'x86_64'],

                'hotswap_os': 0,
                'hotswap_slots': 0,
                'hotswap_free': 0,
                'hotswap_sizes_gb': [],
                'internal_sizes_gb': [466],
            }
        },
    },
    'dfw1': {
        ## dfw1 not used for Ceph
        'name': 'Dallas 01 (Central)',
        'loc_country': 'US',
        'loc_entity': 'TX',
        'loc_city': 'Dallas',

        'logical_path': '/US/TX/Dallas/dfw1',
        'hosts': {}
    },
    'dfw2': {
        ## dfw2 not used for Ceph
        'name': 'Dallas 02 (North)',
        'loc_country': 'US',
        'loc_entity': 'TX',
        'loc_city': 'Dallas',

        'logical_path': '/US/TX/Dallas/dfw2',
        'hosts': {}
    },
    'dfw3': {
        ## dfw3 not used for Ceph
        'name': 'Dallas 02 (Central 2)',
        'loc_country': 'US',
        'loc_entity': 'TX',
        'loc_city': 'Dallas',

        'logical_path': '/US/TX/Dallas/dfw3',
        'hosts': {}
    },
    'ord1': {
        ## ord1 not used for Ceph
        'name': 'Chicago 01',
        'loc_country': 'US',
        'loc_entity': 'IL',
        'loc_city': 'Chicago',

        'logical_path': '/US/IL/Chicago/ord1',
        'hosts': {}
    },
    'fmt1': {
        ## fmt1 not used for Ceph
        'name': 'Fremont 01',
        'logical_path': '/US/CA/Fremont/fmt1',
        'loc_country': 'US',
        'loc_entity': 'CA',
        'loc_city': 'Fremont',

        'hosts': {}
    },
    'atl1': {
        ## atl1 not used for Ceph
        'name': 'Atlanta 01',
        'logical_path': '/US/GA/Atlanta/atl1',
        'loc_country': 'US',
        'loc_entity': 'GA',
        'loc_city': 'Atlanta',

        'hosts': {}
    }
}


def hosts_in_dc(clusters, dc):
    return [h['fqdn'] for k, h in clusters[dc]['hosts'].iteritems()]


def hosts_in_dc_by_tag(clusters, dc, tag):
    return [h['fqdn'] for k, h in clusters[dc]['hosts'].iteritems()
            if tag in h['tags']]


def hosts_in_dc_by_role(clusters, dc, role):
    return [h['fqdn'] for k, h in clusters[dc]['hosts'].iteritems()
            if role in h['roles']]


def hotswap_storage_details(clusters, dc):
    hosts = {}

    for hostname, host in clusters[dc]['hosts'].iteritems():
        start_idx = 1 if host['hotswap_os'] else 0
        host_storage = filter(None, host['hotswap_sizes_gb'][start_idx:])
        hosts[hostname] = {
            'capacity': sum(host_storage),
            'drives': host_storage
        }

    return hosts


def hotswap_storage_capacity(clusters=CLUSTERS, dc=DC):
    return sum([h['capacity'] for k, h in
                hotswap_storage_details(clusters, dc).iteritems()])


def _ceph_ideal_pg_size(replicas=REPLICA_COUNT, osds=OSD_COUNT):
    return (100 * osds) / replicas


fabric.state.output['running'] = False
env.use_ssh_config = True
env.user = 'ceph'
env.hosts = hosts_in_dc(CLUSTERS, DC)
env.roledefs = {
    'mon': hosts_in_dc_by_role(CLUSTERS, DC, 'mon'),
    'mds': hosts_in_dc_by_role(CLUSTERS, DC, 'mds'),
    'osd': hosts_in_dc_by_role(CLUSTERS, DC, 'osd'),
    'local': []
}


@task
@parallel(len(env.hosts))
def uptime():
    run('uptime')


@task
@roles('local')
def capacity():
    total_gb = hotswap_storage_capacity(CLUSTERS, DC)
    total_tb = total_gb / 1024
    print(green('Capacity: %8.2f GB' % total_gb))
    print(green('          %8.2f TB' % total_tb))


@task
def create_user():
    """Creates the ceph user on each of the Ceph nodes, with a disabled
    password and an entry in a sudoers.d file."""

    env.user = 'root'
    run("useradd -m -p '' ceph")
    run("mkdir -p /home/ceph/.ssh")

    with open(expanduser('~/.ssh/id_rsa.pub')) as pubkey:
        append('/home/ceph/.ssh/authorized_keys', pubkey.read())

    run("chown -R ceph.ceph /home/ceph")

    append('/etc/sudoers.d/ceph', 'ceph ALL=(ALL) NOPASSWD:ALL')

    env.user = 'ceph'
    run('uptime')
    run('sudo uptime')


@task
def create_pool(name):
    # TODO
    print(blue('Ideal PG size: %d' % _ceph_ideal_pg_size()))
