from invoke import task, Collection
import logging


@task
def compile(c, compiler="", *files):
    logging.info("Compiling {} with compiler {}".format(
        ", ".join(files), compiler))
