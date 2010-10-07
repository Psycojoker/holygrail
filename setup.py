#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

setup(name='HolyGrail',
      version='0.1 Galahad',
      description='High level lib to manage the holy quests of your life (in other words GTD next actions)',
      author='Laurent Peuch',
      author_email='cortex@worlddomination.be',
      url='http://blog.worlddomination.be/holygrail',
      install_requires=['sqlobject'],
      packages=["holygrail"],
     )

# vim:set shiftwidth=4 tabstop=4 expandtab:
