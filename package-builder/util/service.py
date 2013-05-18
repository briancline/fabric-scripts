from fabric.api import run


def start(service):
    run('service start %s' % service)


def stop(service):
    run('service stop %s' % service)


def restart(service):
    run('service restart %s' % service)


def reload(service):
    run('service reload %s' % service)


def status(service):
    run('service status %s' % service)


def enable(service):
    run('chkconfig %s on' % service)
