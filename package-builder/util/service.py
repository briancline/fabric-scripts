from fabric.api import sudo


def start(service):
    sudo('service %s start' % service)


def stop(service):
    sudo('service %s stop' % service)


def restart(service):
    sudo('service %s restart' % service)


def reload(service):
    sudo('service %s reload' % service)


def status(service):
    sudo('service %s status' % service)


def enable(service):
    sudo('chkconfig %s on' % service)
