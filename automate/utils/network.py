import logging
import os
import random
import socket
from io import StringIO
from pathlib import Path
from typing import Iterable, Optional

import fabric
import keyring
from paramiko.ssh_exception import AuthenticationException
from prompt_toolkit import prompt


def connect(
    host: str,
    user: str,
    port: int = 22,
    identity: Optional[Path] = None,
    passwd_allowed: bool = False,
    passwd_retries: int = 3,
    keyring_allowed: bool = True,
    gateway: Optional[fabric.Connection] = None,
    timeout: int = 30,
) -> fabric.Connection:
    """ Get a fabric connection to a remote host 

        # Arguments
        host: hostname or ip address
        username: on remote host
        port: ssh port for connection
        identity: Path to ssh private key
        passwd_allowed: if True use password if ssh public key authentication fails
        passwd_retries: number of retries for password authentication
        keyring_allowed: if True store passwords in system keyring
        gateway: fabric.Connection to use as gateway
        timeout: timeout for connections in seconds

        # Returns
        a fabric.Connection to the host
    """

    try:
        kwargs = {"key_filename": str(identity.absolute())} if identity else {}
        connection = fabric.Connection(
            host,
            user=user,
            port=port,
            connect_timeout=timeout,
            gateway=gateway,
            connect_kwargs=kwargs,
        )
        connection.open()
    except AuthenticationException as e:
        if passwd_allowed:

            keyring_service = f"automatessh:{host}:{port}"

            for retry in range(passwd_retries):
                password = None
                if retry == 0 and keyring_allowed:
                    password = keyring.get_password(keyring_service, user)
                if password is None:
                    password = prompt(
                        "Password for {}@{}: ".format(user, host),
                        is_password=True,
                    )
                try:
                    connection = fabric.Connection(
                        user=user,
                        host=host,
                        port=port,
                        gateway=gateway,
                        connect_timeout=timeout,
                        connect_kwargs={"password": password},
                    )
                    connection.open()
                except AuthenticationException as e:
                    continue

                if keyring_allowed:
                    keyring.set_password(keyring_service, user, password)
                break
        else:
            raise e

    return connection


def find_local_port() -> int:
    """ Returns a locally bindable port number 

    # Returns
    port number [int]
    """

    while True:
        port = random.randint(1024, 65536)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            return port
        except Exception:
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
munge symlinks=false
"""


def rsync(
    con: fabric.Connection,
    source: str,
    target: str,
    exclude: Iterable[str] = (),
    delete: bool = False,
    verbose: bool = False,
    rsync_opts: str = "",
) -> None:
    """ RSync files or folders to board 

    1. Starts a remote rsync forwards
    2. Forwards rsync server ports over gateway
    3. runs rsync -pthrz <source> <target>
    4. stops remote rsync daemon

    rsync server is run as the connections default user, so can not modify files and folders for which this user does not have access rights 

    # Arguments
    con: fabric.Connection to board
    source: local path should end in "/" if the complete folder is synced
    target: remote_path
    exclude: iterable of exclude patterns
    verbose: if True print transfered files to stdout
    rsync_opts: string of additional rsync options
    """

    local_port = find_local_port()

    with con.forward_local(local_port):
        try:
            con.put(
                StringIO(RSYNC_SPEC.format(port=local_port)),
                "/tmp/rsync-ad-hoc.conf",
            )

            con.run("rsync --daemon --config /tmp/rsync-ad-hoc.conf")
            con.run(f"mkdir -p {target}")

            delete_flag = "--delete" if delete else ""

            exclude_opts = " ".join(["--exclude %s" % e for e in exclude])
            if verbose:
                rsync_opts = "-v " + rsync_opts

            remote_path = f"rsync://localhost:{local_port}/files/{target}"
            rsync_cmd = f"rsync {delete_flag} {exclude_opts} -pthrz {rsync_opts} {source} {remote_path}"
            logging.info("Running {}".format(rsync_cmd))

            con.local(rsync_cmd)
        finally:
            result = con.run("cat /tmp/rsync-ad-hoc.pid", hide="out")
            rsync_pid = result.stdout
            logging.info(f"Killing remote rsync deamon with pid: {rsync_pid}")
            con.run(f"kill  {rsync_pid}", hide="out")
            con.run("rm -f /tmp/rsync-ad-hoc.*")
