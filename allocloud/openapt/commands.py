import logging
import errno
import os
from select import select
from subprocess import Popen, PIPE


LOGGER = logging.getLogger(__name__)


def run_command(command, stdout=None, stderr=None, log_output=False):
    # from https://stackoverflow.com/a/31953436/4578715
    with Popen(command, stdout=PIPE, stderr=PIPE) as process:
        readable = {
            process.stdout.fileno(): stdout, # log separately
            process.stderr.fileno(): stderr,
        }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 1024) # read available
                except OSError as ose:
                    if ose.errno != errno.EIO:
                        raise #XXX cleanup
                    del readable[fd] # EIO means EOF on some systems
                else:
                    if not data: # EOF
                        del readable[fd]
                    else:
                        if log_output:
                            if fd == process.stdout.fileno(): # We caught stdout
                                for line in data.rstrip().split(b'\n'):
                                    LOGGER.debug(line.decode())
                            else: # We caught stderr
                                for line in data.rstrip().split(b'\n'):
                                    LOGGER.error(line.decode())
                        if readable[fd]:
                            readable[fd].write(data)
                            readable[fd].flush()
    return process