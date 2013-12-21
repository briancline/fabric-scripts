#!/usr/bin/env fab -f
# The MIT License (MIT)
#
# Copyright (c) 2013 Brian Cline
# Copyright (c) 2013 SoftLayer Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
import os
import re
import time
import datetime

from fabric.api import task, settings, hide
from fabric.colors import green, red, blue, white
from fabric.operations import local
from prettytable import PrettyTable


EXT_SSH_PORT = 20222
NAT_NET_CIDR = '172.16.2/24'
NAT_EXT_IFACE = 'en0'

DEFAULT_MEMORY = 2048
DEFAULT_CPUS = 2
DEFAULT_OS = 'Ubuntu_64'
DEFAULT_GROUPS = 'OpenStack'
DEFAULT_SOURCE_IMAGE = '/SSD/Images/test-u1204.vdi'

UUID4_REGEX = '([0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})'


def log(message, color=white, bold=False):
    timestamp = datetime.datetime.now().isoformat(' ')
    message = '[%s] %s' % (timestamp, message)
    print(color(message, bold=bold))


def vbox_exec(subcommand, *args):
    #pprint(args)
    command = 'VBoxManage %s %s' % (subcommand, ' '.join(args))
    #log('Executing: %s' % command)

    with settings(hide('output', 'warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        result = local(command, capture=True)

    return result


@task
def os_list():
    os_output = vbox_exec('list ostypes').stdout.split("\n\n")

    columns = ['ID', 'Description', 'Family ID', 'Family Desc', '64-bit']
    table = PrettyTable(columns)
    table.align['ID'] = 'l'
    table.align['Description'] = 'l'

    for os_vomit in os_output:
        lines = os_vomit.splitlines()
        os_info = []
        for line in lines:
            _, value = line.split(':', 1)
            os_info.append(value.strip())
        table.add_row(os)

    table.sortby = 'ID'
    log('\n' + table)


@task
def build(name, groups=DEFAULT_GROUPS, os_type=DEFAULT_OS,
          memory=DEFAULT_MEMORY, cpus=DEFAULT_CPUS,
          source_image=DEFAULT_SOURCE_IMAGE, start=False,
          headless=False):
    groups = ['/%s' % g.strip('/')
              for g in groups.split(';')] if groups else []

    if not os.path.exists(source_image):
        log('Source image "%s" does not exist.', color=red)
        return

    vm_uuid = create_vm(name, groups, os_type)
    configure_vm(vm_uuid, memory, cpus)
    configure_vm_network(vm_uuid)

    target_image = '%s/disk1.vdi' % vm_base_path(vm_uuid)

    if not os.path.exists(target_image):
        copy_disk_image(source_image, target_image)

    configure_vm_storage(vm_uuid, target_image)

    if start:
        start_vm(vm_uuid, headless)


@task
def destroy(vm_name):
    stop_vm(vm_name, wait=True)

    unreg_result = vbox_exec('unregistervm', vm_name, '--delete')
    if unreg_result.return_code != 0:
        raise RuntimeError(unreg_result.stderr)


def vm_off(vm_uuid):
    return 'poweroff' == vm_state(vm_uuid)


def vm_state(vm_uuid):
    state = None
    with settings(warn_only=True):
        state = vm_info(vm_uuid, 'vmstate')
    return state


def vm_info(vm_uuid, key_name):
    info_result = vbox_exec('showvminfo', vm_uuid, '--machinereadable')
    if info_result.return_code != 0:
        raise RuntimeError(info_result.stderr)

    params = {}
    for line in info_result.stdout.splitlines():
        pair = line.split('=', 1)
        params[pair[0].strip('"').lower()] = pair[1].strip('"')

    key_name = key_name.lower()
    if key_name in params:
        return params[key_name]

    return None


def vm_base_path(vm_uuid):
    config_path = vm_info(vm_uuid, 'cfgfile')
    return os.path.dirname(os.path.abspath(config_path))


@task
def start_vm(vm_uuid, headless=False):
    headless_param = '--type headless' if headless else ''

    log('Starting VM...', color=blue, bold=True)
    start_result = vbox_exec('startvm', vm_uuid, headless_param)
    if start_result.return_code != 0:
        raise RuntimeError(start_result.stderr)


@task
def stop_vm(vm_uuid, wait=True):
    log('Stopping VM...', color=blue, bold=True)
    with settings(warn_only=True):
        vbox_exec('controlvm', vm_uuid, 'poweroff')

    while not vm_off(vm_uuid):
        log('Waiting for VM to stop...', color=blue, bold=True)
        time.sleep(1)


def create_vm(name, groups, os_type):
    log('Creating VM...', color=blue, bold=True)

    vm_create_settings = [
        '--name "%s"' % name,
        '--groups "%s"' % ','.join(groups),
        '--ostype %s' % os_type,
        '--register',
    ]

    vm_uuid = None
    create_result = vbox_exec('createvm', *vm_create_settings)
    if create_result.return_code != 0:
        raise RuntimeError(create_result.stderr)

    matches = re.search(UUID4_REGEX, create_result.stdout,
                        flags=re.MULTILINE)
    if not matches:
        log(create_result.stdout, color=red)
        raise RuntimeError('Could not determine new machine UUID!')

    vm_uuid = matches.groups()[0]
    log('New machine created with UUID %s' % vm_uuid, color=green)

    return vm_uuid


def configure_vm(vm_uuid, memory, cpus):
    log('Configuring VM settings...', color=blue, bold=True)

    vm_settings = [
        '--memory %d' % memory,
        '--cpus %d' % cpus,
        '--vram 16',
        '--accelerate3d off',
        '--accelerate2dvideo off',
        '--acpi on',
        '--ioapic on',
        '--hwvirtex on',
        '--boot1 disk --boot2 net',
        '--audio none',
        '--clipboard disabled',
        '--defaultfrontend gui',
    ]

    modify_result = vbox_exec('modifyvm', vm_uuid, *vm_settings)
    if modify_result.return_code != 0:
        raise RuntimeError(modify_result.stderr)

    return True


def configure_vm_network(vm_uuid):
    log('Configuring networking...', color=blue, bold=True)

    nic_settings = [
        '--nic1 nat',
        '--cableconnected1 on',
        '--natnet1 %s' % NAT_NET_CIDR,
        '--natdnshostresolver1 on',
        '--natpf1 "sshd,tcp,,%d,,22"' % EXT_SSH_PORT,

        '--nic2 bridged',
        '--cableconnected2 on',
        '--bridgeadapter2 %s' % NAT_EXT_IFACE,
    ]

    modify_result = vbox_exec('modifyvm', vm_uuid, *nic_settings)
    if modify_result.return_code != 0:
        raise RuntimeError(modify_result.stderr)

    return True


def configure_vm_storage(vm_uuid, disk_path):
    log('Configuring storage controllers...', color=blue, bold=True)

    ctrl_settings = [
        '--name ctl00',
        '--add sata',
        '--portcount 6',
        '--hostiocache off',
        '--bootable on',
    ]

    modify_result = vbox_exec('storagectl', vm_uuid, *ctrl_settings)
    if modify_result.return_code != 0:
        raise RuntimeError(modify_result.stderr)

    # Attach disk to the new controller
    log('Configuring storage devices...', color=blue, bold=True)

    disk_attach_settings = [
        '--storagectl ctl00',
        '--port 0',
        '--type hdd',
        '--medium %s' % disk_path,
    ]

    modify_result = vbox_exec('storageattach', vm_uuid, *disk_attach_settings)
    if modify_result.return_code != 0:
        raise RuntimeError(modify_result.stderr)


def copy_disk_image(source_image, target_image):
    log('Copying base OS image...', color=blue, bold=True)

    clone_settings = [
        '"%s"' % source_image,
        '"%s"' % target_image,
        '--format VDI',
    ]

    clone_result = vbox_exec('clonehd', *clone_settings)
    if clone_result.return_code != 0:
        raise RuntimeError(clone_result.stderr)
