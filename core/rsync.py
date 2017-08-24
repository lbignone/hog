from subprocess import check_output


def rsync(origin, destination):
    """ Sync two paths. If any path is of the form geryon:<path> it uses ssh to
    transfer data to work properly remote hosts have to be configured at
    .ssh/config or similar"""

    if ':' in origin:
        origin = ['-e', 'ssh', origin]
    else:
        origin = [origin]
    if ':' in destination:
        destination = ['-e', 'ssh', destination]
    else:
        destination = [destination]

    cmd = ['rsync', '-avz']
    cmd += origin + destination
    cmd += ['--progress']
    output = check_output(cmd)
    return output
