from fabric.api import sudo
from patchwork.environment import has_binary


def _service_command(service_name):
    command = '/etc/init.d/%s'
    if has_binary('service', runner=sudo):
        command = 'service %s'
    return command % service_name


def _service_exec(service_name, command):
    return sudo('%s %s' % (_service_command(service_name), command))


def start(service):
    return _service_exec(service, 'start')


def stop(service):
    return _service_exec(service, 'stop')


def restart(service):
    return _service_exec(service, 'restart')


def reload(service):
    return _service_exec(service, 'reload')


def status(service):
    return _service_exec(service, 'status')


def enable(service):
    # TODO: add debian and ubuntu commands
    sudo('chkconfig %s on' % service)
