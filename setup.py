#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='HolyGrail',
      version='0.2 Perceval',
      description='High level lib to manage the holy quests of your life (in other words GTD next actions)',
      author='Laurent Peuch',
      long_description=open("README.rst").read(),
      author_email='cortex@worlddomination.be',
      url='http://blog.worlddomination.be/holygrail',
      install_requires=['sqlobject'],
      packages=["holygrail"],
      license = "aGPLv3+",
      keywords="gtd lib holygrail",
     )

# vim:set shiftwidth=4 tabstop=4 expandtab:
