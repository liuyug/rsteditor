#!/usr/bin/env python
# -*- coding:utf-8 -*-

def strsize2intlist(size, default=[]):
    s = [int(v) for v in size.split('x')]
    if not s:
        s = default
    return s

