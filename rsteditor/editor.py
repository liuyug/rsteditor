#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import keyword

import wx
import wx.stc
import wx.lib.newevent

_ = wx.GetTranslation

try:
    import configparser
except:
    import ConfigParser as configparser

from rsteditor import CONFIG_PATH
from rsteditor import STYLE_FILE

ReqPreviewEvent, EVT_REQ_PREVIEW = wx.lib.newevent.NewCommandEvent()
FindCloseEvent, EVT_FIND_CLOSE = wx.lib.newevent.NewCommandEvent()
FindPrevEvent, EVT_FIND_PREV = wx.lib.newevent.NewCommandEvent()
FindNextEvent, EVT_FIND_NEXT = wx.lib.newevent.NewCommandEvent()
ScrollWinEvent, EVT_SCROLL_WIN = wx.lib.newevent.NewCommandEvent()

ID_BASE = wx.ID_HIGHEST + 1
ID_SEARCH_TEXT = ID_BASE + 1
ID_MATCH_WHOLE_WORD = ID_BASE + 2
ID_MATCH_CASE = ID_BASE + 3
ID_MATCH_WORD_START = ID_BASE + 4
ID_BUTTON_CLOSE = ID_BASE + 5
ID_BUTTON_FIND = ID_BASE + 6

class FindDialog(wx.Dialog):
    """ Find dialog for STC """
    def __init__(self, *args, **kwargs):
        super(FindDialog, self).__init__(*args, **kwargs)
        topbox = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.StaticText(self, label=_('Search For:')),
                0, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(wx.TextCtrl(self, id=ID_SEARCH_TEXT, size=(300,-1)),
                1, wx.ALL|wx.ALIGN_LEFT, 5)
        topbox.Add(box, 0, wx.EXPAND|wx.ALL, 5)
        topbox.Add(wx.CheckBox(self, id=ID_MATCH_WHOLE_WORD, label=_('Match &whole word')),
                   0, wx.ALL|wx.ALIGN_LEFT, 5)
        topbox.Add(wx.CheckBox(self, id=ID_MATCH_CASE, label=_('&Match case')),
                   0, wx.ALL|wx.ALIGN_LEFT, 5)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.Button(self, id=ID_BUTTON_CLOSE, label=_('&Close')),
                0, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(wx.Button(self, id=ID_BUTTON_FIND, label=_('Find')),
                0, wx.ALL|wx.ALIGN_CENTER, 5)
        topbox.Add(box, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        self.SetSizer(topbox)
        topbox.SetSizeHints(self)
        # set ESC key to click close button
        self.SetEscapeId(ID_BUTTON_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.OnFind, id=ID_BUTTON_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.OnFind, id=ID_BUTTON_FIND)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        wx.FindWindowById(ID_BUTTON_FIND, self).SetDefault()

    def OnFind(self, event):
        """ handle find button event and forward to parent """
        id = event.GetId()
        if id == ID_BUTTON_CLOSE:
            evt = FindCloseEvent(id=ID_BUTTON_CLOSE)
        elif id == ID_BUTTON_FIND:
            evt = FindNextEvent(id=ID_BUTTON_FIND)
        else:
            return
        self.GetParent().GetEventHandler().ProcessEvent(evt)

    def OnClose(self, event):
        """ handle dialog close event """
        evt = FindCloseEvent(id=ID_BUTTON_CLOSE)
        self.GetParent().GetEventHandler().ProcessEvent(evt)

    def GetFlags(self):
        flags = 0
        if wx.FindWindowById(ID_MATCH_WHOLE_WORD, self).GetValue():
            flags |= wx.stc.STC_FIND_WHOLEWORD
        if wx.FindWindowById(ID_MATCH_CASE, self).GetValue():
            flags |= wx.stc.STC_FIND_MATCHCASE
        return flags

    def GetText(self):
        """ return search text """
        return wx.FindWindowById(ID_SEARCH_TEXT, self).GetValue()


class EditorWindow(wx.stc.StyledTextCtrl):
    """ RSTEditor editor window """
    def __init__(self, *args, **kwargs):
        super(EditorWindow, self).__init__(*args, **kwargs)
        self.styles = self.ReadStyleConfig()
        self.SetStyle()
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0, 30)
        self.SetMarginWidth(1, 5)
        self.SetUseTabs(0)
        self.SetTabWidth(4)
        self.SetIndentationGuides(1)
        self.SetIndent(4)
        self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        self.SetEdgeColumn(78)
        self.SetWrapMode(1)
        self.SetCodePage(65001)
        self.StyleClearAll()
        self.FindDlg = FindDialog(self, title=_('Find'))
        self.Bind(EVT_FIND_CLOSE, self.OnFind)
        self.Bind(EVT_FIND_PREV, self.OnFind)
        self.Bind(EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        self.char_count = 0

    def OnFind(self, event):
        """ handle find event """
        id = event.GetId()
        if id == ID_BUTTON_CLOSE:
            pass
        elif id == ID_BUTTON_FIND:
            flags = self.FindDlg.GetFlags()
            text = self.FindDlg.GetText()
            self.SearchAnchor()
            pos = self.SearchNext(flags, text)
            if pos > 0:
                self.EnsureCaretVisible()
        self.FindDlg.Hide()

    def OnKeyUp(self, event):
        if self.char_count > 1 and event.GetKeyCode() == wx.WXK_RETURN:
            evt = ReqPreviewEvent(id=self.GetId())
            wx.PostEvent(self, evt)
            self.char_count = 0
        event.Skip()

    def OnChar(self, event):
        self.char_count += 1
        if self.char_count > 5:
            evt = ReqPreviewEvent(id=self.GetId())
            wx.PostEvent(self, evt)
            self.char_count = 0
        event.Skip()

    def OnScroll(self, event):
        orien = event.GetOrientation()
        pos = event.GetPosition()
        if orien == wx.VERTICAL:
            evt = ScrollWinEvent(pos=pos, id=self.GetId())
            wx.PostEvent(self, evt)
        event.Skip()

    def GetValue(self):
        """ get all text """
        return self.GetTextUTF8()

    def SetValue(self, text):
        """ set all text """
        if not isinstance(text, unicode):
            text = text.decode('utf-8', 'ignore')
        self.SetText(text)
        self.GotoPos(0)
        self.EmptyUndoBuffer()

    def ShowFindWindow(self):
        """ only show find dialog """
        wx.FindWindowById(ID_SEARCH_TEXT, self.FindDlg).SetFocus()
        self.FindDlg.Center()
        self.FindDlg.Show(True)

    def FindNext(self):
        flags = self.FindDlg.GetFlags()
        text = self.FindDlg.GetText()
        start, end = self.GetSelection()
        self.GotoPos(end)
        self.SearchAnchor()
        pos = self.SearchNext(flags, text)
        if pos > 0:
            self.EnsureCaretVisible()
        else:
            self.SetSelection(start, end)
        return

    def FindPrev(self):
        flags = self.FindDlg.GetFlags()
        text = self.FindDlg.GetText()
        start, end = self.GetSelection()
        self.GotoPos(start)
        self.SearchAnchor()
        pos = self.SearchPrev(flags, text)
        if pos > 0:
            self.EnsureCaretVisible()
        else:
            self.SetSelection(start, end)
        return

    def SetStyle(self, type='default'):
        style = 'default'
        self.StyleClearAll()
        if type == '.py':
            style = 'python'
            self.SetLexer(wx.stc.STC_LEX_PYTHON)
            self.SetKeyWords(0, ' '.join(keyword.kwlist))
        elif type in ['.html', '.htm', '.php', '.asp']:
            style = 'html'
            self.SetLexer(wx.stc.STC_LEX_HTML)
        elif type in ['.rst', '.rest']:
            style = 'default'
        for n in self.styles[style]:
            v = self.styles[style][n]
            self.StyleSetSpec(n, v)
        return

    def ReadStyleConfig(self):
        style_file = os.path.join(CONFIG_PATH, STYLE_FILE)
        if not os.path.exists(style_file):
            raise Exception('Not found %s'% STYLE_FILE)
            return
        style_config = configparser.ConfigParser()
        style_config.read(style_file)
        styles = {}
        for sec in style_config.sections():
            style = {}
            for n, v in style_config.items(sec):
                stylenumber = int(n.split('.')[-1])
                style[stylenumber] = v
            styles[sec] = style
        return styles


class CodeViewer(EditorWindow):
    """ code viewer """
    def __init__(self, *args, **kwargs):
        super(CodeViewer, self).__init__(*args, **kwargs)
        self.SetStyle('.html')
        self.SetReadOnly(True)

    def SetValue(self, text):
        """ set all readonly text """
        self.SetReadOnly(False)
        super(CodeViewer, self).SetValue(text)
        self.SetReadOnly(True)
