from invoke import task
from tabulate import tabulate


@task()
def list_kernels(c, commandline=False):
    "List currently activated kernel version and commandlines for all boards"

    table = []
    for board in c.boards():
        table_line = [board.name]

        try:
            with board.connect() as con:
                result = con.run("uname -r", hide=True, warn=True)

                version = ""
                if result.ok:
                    version = result.stdout.strip()
                    table_line.append(version)
                else:
                    table_line.append("unknown")

                configs = ""
                for kernel in board.os.kernels:
                    if kernel.version == version:
                        configs += kernel.name + " "

                configs = configs.strip()
                table_line.append(configs)

                if commandline:
                    result = con.run("cat /proc/cmdline", hide=True, warn=True)

                    if result.ok:
                        table_line.append(result.stdout.strip())
                    else:
                        table_line.append("unknown")
        except Exception as e:
            print(str(e))

        table.append(table_line)

    headers = ["Board", "Kernel Version", "Kernel Configs"]

    if commandline:
        headers.append("Kernel Commandline")

    print(tabulate(table, headers=headers))
