from setuptools import setup

import sys
import os
import subprocess

with open(os.path.join(os.path.dirname(__file__), "oplus", "version.txt")) as f:
    version = f.read().strip()


if sys.argv[-3] == 'tag':
    user = sys.argv[-2]
    pwd = sys.argv[-1]
    output = subprocess.Popen('git tag -a %s -m "version %s" ' % (version, version), shell=True, stderr=subprocess.PIPE)
    os.system('git tag -d $(git tag --list "jenkins*")')
    #    os.system('git commit -m "version updated via setup.py tag"')
    err = output.communicate()[1]
    if err != b'':
        raise ValueError('"git tag" failed, the tag might already exist')
    os.system('git push https://%s:%s@github.com/Openergy/oplus.git --tags' % (user, pwd))
    sys.exit()

setup(
    name='oplus',

    version=version,

    packages=['oplus'],

    author="Geoffroy d'Estaintot",

    author_email="geoffroy.destaintot@openergy.fr",

    long_description=open('README.md').read(),

    install_requires=[
        'pandas',
        'plotly'
        ],

    url='https://github.com/Openergy/oplus',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
    ],

    keywords=['data', 'simulation'],

    package_data={'oplus': ['*.txt']},

    include_package_data=True
)
