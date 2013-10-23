#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

import gobject
gobject.threads_init()

import pygtk
pygtk.require('2.0')
import gtk, gtk.gdk

# pywebkitgtk (http://code.google.com/p/pywebkitgtk/)
import webkit

'''
As far as I know (I may be wrong), a wx.Panel is "composed" by a GtkPizza
as a child of GtkScrolledWindow. GtkPizza is a custom widget created for
wxGTK.

WebKitGTK+ - the webkit port for GTK+ that has python bindings - wants a
GtkScrolledWindow as parent.

So all we need to embed webkit in wxGTK is find the wx.Panel's
GtkScrolledWindow.
This is acomplished using pygtk that is present in major distro's by
default, at least those that use gnome as its main desktop environment.

A last note is that for get a handle of a window in X, the window must be
"realized" first, in other words, must already exists. So we must Show
the wx.Frame before use this WKHtmlWindow class.

'''
class WKHtmlWindow(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)

        # Here is where we do the "magic" to embed webkit into wxGTK.
        whdl = self.GetHandle()
        window = gtk.gdk.window_lookup(whdl)

        # We must keep a reference of "pizza". Otherwise we get a crash.
        self.pizza = pizza = window.get_user_data()

        self.scrolled_window = scrolled_window = pizza.parent

        # Removing pizza to put a webview in it's place
        scrolled_window.remove(pizza)

        self.ctrl = ctrl = webkit.WebView()
        scrolled_window.add(ctrl)

        self.hadj = self.scrolled_window.get_hadjustment()
        self.vadj = self.scrolled_window.get_vadjustment()

        #self.vadj.connect('value-changed', self.OnValueChanged)
        #self.vadj.connect('changed', self.OnChanged)
        self.ctrl.connect('load-finished', self.OnLoadFinished)

        settings = self.ctrl.get_settings()
        settings.set_property('enable-default-context-menu', False)
        #d = settings.get_property('default-font-family')

        self.delay_do_scroll = False
        self.dx = 0
        self.dy = 0

        scrolled_window.show_all()

    def OnValueChanged(self, adj):
        print('value changed', adj.get_value())

    def OnChanged(self, adj):
        print('changed', adj.get_value())

    def OnLoadFinished(self, frame, data):
        if self.delay_do_scroll:
            self.DoScrollWindow(self.dx, self.dy)
            self.delay_do_scroll = False

    # Some basic usefull methods
    def SetEditable(self, editable=True):
        self.ctrl.set_editable(editable)

    def LoadUrl(self, url):
        self.ctrl.load_uri(url)

    def HistoryBack(self):
        self.ctrl.go_back()

    def HistoryForward(self):
        self.ctrl.go_forward()

    def StopLoading(self):
        self.ctrl.stop_loading()

    def SetPage(self, html, url=None):
        """ for pywebkitgtk """
        if not url:
            url = ''
        self.ctrl.load_string(html, 'text/html', 'utf-8', url)

    def DoScrollWindow(self, dx, dy):
        self.hadj.set_value(dx)
        self.vadj.set_value(dy)

    def ScrollWindow(self, dx, dy, delay=False):
        if delay:
            self.DelayScrollWindow(dx, dy)
        else:
            self.DoScrollWindow(dx, dy)

    def GetViewStart(self):
        dx = self.hadj.get_value()
        dy = self.vadj.get_value()
        return (dx, dy)

    def GetViewRange(self):
        dx = self.hadj.get_upper()
        dy = self.vadj.get_upper()
        return (dx, dy)

    def DelayScrollWindow(self, dx, dy):
        self.delay_do_scroll = True
        self.dx = dx
        self.dy = dy

