#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx.lib.newevent
from rsteditor import HtmlViewer

ReqScrollEvent, EVT_REQ_SCROLL = wx.lib.newevent.NewCommandEvent()

class WebViewer(HtmlViewer):
    """ RSTEditor WebViewer window """
    def __init__(self, *args, **kwargs):
        super(WebViewer, self).__init__(*args, **kwargs)
        self.Bind(EVT_REQ_SCROLL, self.OnReqScroll)

    def OnReqScroll(self, event):
        dx = event.dx
        dy = event.dy
        delay = event.delay
        self.ScrollWindow(dx, dy, delay)

