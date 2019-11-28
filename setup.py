from setuptools import setup, find_packages

setup(
    name="automate",
    version="0.1",
    packages=["automate"],
    entry_points={
        'console_scripts': ['automate = automate.main:program.run']
    }
)
