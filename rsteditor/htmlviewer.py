#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.lib.newevent

try:
    if wx.version().startswith('2.9'):
        from wx.html2 import WebView as HtmlViewer
    elif wx.Platform == '__WXGTK__':
        from rsteditor.webkit_gtk import WKHtmlWindow as HtmlViewer
    elif wx.Platform == '__WXMSW__':
        from wx.lib.iewin import IEHtmlWindow as HtmlViewer
    elif wx.Platform == '__WXMAC__':
        from wx.webkit import WebKitCtrl as HtmlViewer
except:
    from wx.html import HtmlWindow as HtmlViewer


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
        if wx.version().startswith('2.9'):
            super(WebViewer, self).ScrollWindow(dx, dy)
        elif wx.Platform == '__WXGTK__':
            super(WebViewer, self).ScrollWindow(dx, dy, delay)
        elif wx.Platform == '__WXMSW__':
            # iewin don't support scroll
            pass
        elif wx.Platform == '__WXMAC__':
            # wait to test
            pass
        else:
            super(WebViewer, self).Scroll(dx, dy)
        return

    def SetPage(self, html, url=None):
        if wx.version().startswith('2.9'):
            super(WebViewer, self).SetPage(html, url)
        elif wx.Platform == '__WXGTK__':
            super(WebViewer, self).SetPage(html, url)
        elif wx.Platform == '__WXMSW__':
            super(WebViewer, self).LoadString(html)
        elif wx.Platform == '__WXMAC__':
            # wait to test
            pass
        else:
            super(WebViewer, self).SetPage(html)
        return

def GetWebViewer(*args, **kwargs):
    """ Create WebViewer """
    if wx.version().startswith('2.9'):
        wv = HtmlViewer.New(*args, **kwargs)
        print(wv)
        return wv
    else:
        return
        return WebViewer(*args, **kwargs)

