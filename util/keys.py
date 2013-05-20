from os.path import exists, expanduser
from fabric.api import run, task, warn_only
from fabric.colors import red
from fabric.contrib import files


@task
def push_key(custom_key=None, user_name=''):
    key_names = ['id_dsa.pub',
                 'id_rsa.pub']

    if custom_key:
        key_names = [custom_key]

    local_key = None
    for key_file in key_names:
        key_path = expanduser('~/.ssh/%s' % key_file)
        if exists(key_path):
            local_key = key_path
            break

    if not local_key:
        print(red('No local keys found.'))
        return

    key = open(local_key).read().strip()
    with warn_only():
        run('mkdir -p ~%s/.ssh && chmod 700 ~%s/.ssh' % (user_name, user_name))
        # TODO: $HOME used with append due to a fabric bugfix pending release.
        #       The ~ gets quoted as a literal when it performs an egrep.
        #       Fix should be available in 1.6.1 or 1.7.0, whichever is next.
        home_dir = '/home/%s' % user_name if user_name else '$HOME'
        files.append('%s/.ssh/authorized_keys' % home_dir, key, partial=True)
