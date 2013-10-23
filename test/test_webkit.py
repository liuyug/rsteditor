#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import wxversion
#wxversion.select("2.6")
wxversion.select("2.8")

import wx

from rsteditor.webkit_gtk import WKHtmlWindow as HtmlWindow

class TestWKPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.html = HtmlWindow(self)
        self.html.SetEditable(True)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.html, 1, wx.EXPAND)

        subbox = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(self, -1, "Load File")
        self.Bind(wx.EVT_BUTTON, self.OnLoadFile, btn)
        subbox.Add(btn, 1, wx.EXPAND | wx.ALL, 2)

        btn = wx.Button(self, -1, "Load URL")
        self.Bind(wx.EVT_BUTTON, self.OnLoadURL, btn)
        subbox.Add(btn, 1, wx.EXPAND | wx.ALL, 2)

        btn = wx.Button(self, -1, "Back")
        self.Bind(wx.EVT_BUTTON, self.OnBack, btn)
        subbox.Add(btn, 1, wx.EXPAND | wx.ALL, 2)

        btn = wx.Button(self, -1, "Forward")
        self.Bind(wx.EVT_BUTTON, self.OnForward, btn)
        subbox.Add(btn, 1, wx.EXPAND | wx.ALL, 2)

        btn = wx.Button(self, -1, "Scroll")
        self.Bind(wx.EVT_BUTTON, self.OnScroll, btn)
        subbox.Add(btn, 1, wx.EXPAND | wx.ALL, 2)

        self.box.Add(subbox, 0, wx.EXPAND)
        self.SetSizer(self.box)
        self.Layout()

    def OnLoadFile(self, event):
        dlg = wx.FileDialog(self, wildcard = '*.htm*', style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.html.LoadUrl("file://%s" % path)

        dlg.Destroy()

    def OnLoadURL(self, event):
        dlg = wx.TextEntryDialog(self, "Enter a URL", defaultValue="http://")

        if dlg.ShowModal() == wx.ID_OK:
            url = dlg.GetValue()
            if not url.startswith('http://'):
                url = "http://%s" % url
            self.html.LoadUrl(url)

        dlg.Destroy()

    def OnBack(self, event):
        self.html.HistoryBack()

    def OnForward(self, event):
        self.html.HistoryForward()

    def OnScroll(self, event):
        self.html.ScrollBottom()

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.Show()

        TestWKPanel(self)

        # This is need it for wxPython2.8,
        # for 2.6 doesnt hurt
        self.SendSizeEvent()


def main():
    app = wx.App()
    f = Frame()
    app.MainLoop()

if __name__ == '__main__':
    main()

