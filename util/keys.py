from os.path import exists, expanduser
from fabric.api import run, task, warn_only
from fabric.colors import red
from fabric.contrib import files


@task
def push_key():
    key_path = expanduser('~/.ssh/id_rsa.pub')
    if not exists(key_path):
        print(red('%s not found.' % key_path))
        return

    key = open(key_path).read().strip()
    with warn_only():
        run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        # TODO: $HOME used with append due to a fabric bugfix pending release
        #       Should be available in 1.6.1 or 1.7.0, whichever is next.
        files.append('$HOME/.ssh/authorized_keys', key, partial=True)
