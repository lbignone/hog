from subprocess import check_output


def ssh_folder(origin, destination):
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
    print(cmd)
    r = check_output(cmd)
    return r
