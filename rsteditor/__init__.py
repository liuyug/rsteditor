#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path

import wx

_ = wx.GetTranslation

APPNAME = 'RSTEditor'
VERSION = '1.0.0a'
AUTHORS =['Yugang LIU',]

HOME_PATH = os.path.join(os.environ['HOME'])
BASE_PATH = os.path.join(HOME_PATH, '.config', APPNAME.lower())
CONFIG_PATH = os.path.join(BASE_PATH, 'config')
TEMPLATE_PATH = os.path.join(BASE_PATH, 'template')

STYLE_FILE = 'styles.ini'
CONFIG_FILE = 'config.ini'

FILENAME = 'Unknown.rst'
ALLOWED_LOADS = ['.rst', '.rest',
        '.html', '.htm',
        '.txt',
        '.c', '.cpp', '.h',
        '.sh',
        '.py']

DATA_PATH = ''

if wx.Platform == '__WXGTK__':
    from rsteditor.webkit_gtk import WKHtmlWindow as HtmlViewer
    DATA_PATH = os.path.join('/usr/share/%s'% APPNAME.lower())
elif wx.Platform == '__WXMSW__':
    DATA_PATH = ''
else:
    from wx.html import HtmlWindow as HtmlViewer

try:
    import configparser
except:
    import ConfigParser as configparser

config = configparser.ConfigParser()

