#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from docutils.core import publish_string
except:
    raise Exception('Please install docutilis firstly')

def rst2html(rst_text):
    try:
        output = publish_string(rst_text, writer_name='html')
        return output
    except Exception as err:
        print(err)
    return ''
