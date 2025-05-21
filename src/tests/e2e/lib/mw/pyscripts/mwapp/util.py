# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\util.py
import os
import subprocess
import tempfile
import time
import re

def run_remote_cmd(user, host, cmd):
    """ run_remote_cmd(user, host, cmd)
    
        Run a command on a remote host using ssh
    
        @param user: {str} - User name to use for authentication
        @param host: {str} - Host address to connect to
        @param cmd: {str} - Command line runnable string
        @return {tuple} - stdout and stderr output strings
    """
    dest = '{0}@{1}'.format(user, host)
    cmd_list = ['ssh',
     '-q',
     dest,
     cmd]
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        raise Exception(stderr)
    return stdout


def scp(source, dest):
    """ scp(source, dest)
    
        Wrapper function that calls scp using the subprocess module. If accessing a
        remote file use the following template.
            user@host:<path>
    
        @param source: {str} - Source file path
        @param dest: {str} - Destination file path
        @return {tuple} - stdout and stderr output strings
    """
    cmd_list = ['scp',
     '-B',
     source,
     dest]
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        raise Exception(stderr)
    return stdout


def send_file(contents, dest_path):
    """ send_file(contents, dest_path)
    
        Send file contents to the host and path specified in dest_path
    
        dest_path should have the form <user>@<host>:<path>
    
        @param contents: {str} - String buffer containing file data
        @param dest_path: {str} - File path to be written to on remote host
    """
    fd, path = tempfile.mkstemp()
    with open(path, 'w') as f:
        f.write(contents)
    try:
        scp(path, dest_path)
    except:
        raise
    finally:
        os.close(fd)
        os.unlink(path)


def cleanup_old_files(number_days, file_path, file_wildcard):
    num_files_removed = 0
    time_in_secs = time.time() - int(number_days) * 24 * 60 * 60
    for f in os.listdir(file_path):
        full_path = os.path.join(file_path, f)
        if re.search(file_wildcard, full_path) and os.stat(full_path).st_mtime <= time_in_secs:
            os.remove(full_path)
            num_files_removed += 1

    return num_files_removed