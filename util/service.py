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


def reload_config(service):
    return _service_exec(service, 'reload')


def status(service):
    return _service_exec(service, 'status')


def enable(service, runlevels='345'):
    if has_binary('update-rc.d', runner=sudo):
        return sudo('update-rc.d enable %s %s' % (service, runlevels))
    elif has_binary('chkconfig', runner=sudo):
        return sudo('chkconfig %s on' % service)
    else:
        raise NotImplementedError('update-rc.d nor chkconfig not found!')


def disable(service, runlevels='345'):
    if has_binary('update-rc.d', runner=sudo):
        return sudo('update-rc.d disable %s %s' % (service, runlevels))
    elif has_binary('chkconfig', runner=sudo):
        return sudo('chkconfig %s off' % service)
    else:
        raise NotImplementedError('update-rc.d nor chkconfig not found!')
