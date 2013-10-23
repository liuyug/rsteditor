#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
from distutils.core import setup
import distutils.command.install_scripts

from rsteditor import APPNAME
from rsteditor import VERSION

class my_install(distutils.command.install_scripts.install_scripts):
    """ remove script ext """
    def run(self):
        distutils.command.install_scripts.install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                os.rename(script, script[:-3])

with open('README.rst') as f:
    long_description=f.read()

setup(name=APPNAME.lower(),
      version=VERSION,
      author='Yugang LIU',
      author_email='liuyug@gmail.com',
      url='https://github.com/liuyug/',
      license='GPLv3',
      description='Editor for ReStructedText',
      long_description=long_description,
      platforms=['noarch'],
      packages=[
          'rsteditor',
      ],
      package_dir = {'rsteditor': 'rsteditor'},
      data_files = [
          ('share/%s'% APPNAME.lower(), [
              'README.rst',
              'MANIFEST.in',
              'test.py']),
          ('share/%s/config'% APPNAME.lower(), ['config/styles.ini']),
          ],
      scripts=['rsteditor.py'],
      requires=['docutils', 'wxPython', 'pygtk', 'pywebkitgtk'],
      cmdclass = {"install_scripts": my_install},
      )


