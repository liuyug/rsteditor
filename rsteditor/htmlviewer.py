#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx.html
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
        if isinstance(self, wx.html.HtmlWindow):
            super(WebViewer, self).Scroll(dx, dy)
        elif isinstance(self, wx.lib.iewin.IEHtmlWindow):
            super(WebViewer, self).ScrollWindow(dx, dy)
        else:
            super(WebViewer, self).ScrollWindow(dx, dy, delay)

    def SetPage(self, html, url=None):
        if isinstance(self, wx.html.HtmlWindow):
            super(WebViewer, self).SetPage(html)
        elif isinstance(self, wx.lib.iewin.IEHtmlWindow):
            super(WebViewer, self).LoadString(html)
        else:
            super(WebViewer, self).SetPage(html, url)
