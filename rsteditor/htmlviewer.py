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
        if wx.Platform == '__WXGTK__':
            super(WebViewer, self).ScrollWindow(dx, dy, delay)
        elif wx.Platform == '__WXMSW__':
            super(WebViewer, self).ScrollWindow(dx, dy)
        elif wx.Platform == '__WXMAC__':
            pass
        else:
            super(WebViewer, self).Scroll(dx, dy)
        return

    def SetPage(self, html, url=None):
        if wx.Platform == '__WXGTK__':
            super(WebViewer, self).SetPage(html, url)
        elif wx.Platform == '__WXMSW__':
            super(WebViewer, self).LoadString(html)
        elif wx.Platform == '__WXMAC__':
            pass
        else:
            super(WebViewer, self).SetPage(html)
        return
