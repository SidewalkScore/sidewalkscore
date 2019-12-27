# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='sidewalkscore',
    version='0.1.0',
    description='SidewalkScore, a network-based foundation for walkability metrics.',
    python_requires='==3.*,>=3.6.0',
    author='Nick Bolten',
    license='apache-2.0',
    entry_points={
        "console_scripts": ["sidewalkscore = sidewalkscore:cli.sidewalkscore"]
    },
    packages=['sidewalkscore'],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        'entwiner', 'pre-commit==1.*,>=1.20.0', 'shapely==1.*,>=1.6.0',
        'unweaver'
    ],
    dependency_links=[
        'git+https://github.com/nbolten/entwiner.git@4cacee4#egg=entwiner',
        'git+https://github.com/nbolten/unweaver.git@0f10383#egg=unweaver'
    ],
    extras_require={"dev": ["black==18.9b0", "pytest==5.*,>=5.2.0"]},
)
