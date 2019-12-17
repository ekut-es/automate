import logging
import os
import random
import socket
from io import StringIO
from typing import Iterable

import fabric


def find_local_port() -> int:
    """ Returns a locally bindable port number """

    while True:
        port = random.randint(1024, 65536)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            return port
        except:
            logging.debug("Port {} is not bindable".format(port))


RSYNC_SPEC = """
port={port}
use chroot=false
log file=/tmp/rsync-ad-hoc.log
pid file=/tmp/rsync-ad-hoc.pid
[files]
max verbosity=4
path=/
read only=false
"""


def rsync(
    con: fabric.Connection,
    source: str,
    target: str,
    exclude: Iterable[str] = (),
    delete: bool = False,
    rsync_opts: str = "",
) -> None:

    local_port = find_local_port()

    with con.forward_local(local_port):
        try:
            con.put(
                StringIO(RSYNC_SPEC.format(port=local_port)),
                "/tmp/rsync-ad-hoc.conf",
            )

            con.run("rsync --daemon --config /tmp/rsync-ad-hoc.conf")

            delete_flag = "--delete" if delete else ""

            exclude_opts = " ".join(["--exclude %s" % e for e in exclude])

            remote_path = f"rsync://localhost:{local_port}/files/{target}"
            rsync_cmd = f"rsync {delete_flag} {exclude_opts} -pthrvz {rsync_opts} {source} {remote_path}"
            logging.info("Running {}".format(rsync_cmd))

            con.local(rsync_cmd)
        finally:
            result = con.run("cat /tmp/rsync-ad-hoc.pid", hide="out")
            rsync_pid = result.stdout
            logging.info(f"Killing remote rsync deamon with pid: {rsync_pid}")
            con.run(f"kill  {rsync_pid}", hide="out")
            con.run("rm -f /tmp/rsync-ad-hoc.*")
