#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil

import wx
import wx.lib.newevent

from rsteditor import _

ID_BASE = wx.ID_HIGHEST + 1
ID_NEW_DIRECTORY = ID_BASE + 1
ID_RENAME = ID_BASE + 2
ID_DELETE = ID_BASE + 3
ID_REFRESH = ID_BASE + 4


LoadFileEvent, EVT_LOAD_FILE = wx.lib.newevent.NewCommandEvent()
SetRootEvent, EVT_SET_ROOT = wx.lib.newevent.NewCommandEvent()

class ExplorerWindow(wx.TreeCtrl):
    """ file explorer"""
    def __init__(self, *args, **kwargs):
        super(ExplorerWindow, self).__init__(id=wx.ID_ANY, style=wx.TR_DEFAULT_STYLE, *args, **kwargs)
        self.imagelist = wx.ImageList(16, 16)
        self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, size=(16, 16)))
        self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, size=(16, 16)))
        self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, size=(16, 16)))
        self.SetImageList(self.imagelist)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivate)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.OnItemCollapsing)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(EVT_SET_ROOT, self.OnSetRoot)
        self.rootid = wx.TreeItemId()
        self.rootdir = ''
        # popup menu
        self.popup_menu = wx.Menu()
        self.popup_menu.Append(wx.ID_NEW, _('&New'))
        self.popup_menu.Append(ID_NEW_DIRECTORY, _('New &directory'))
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(ID_RENAME, _('&Rename...'))
        self.popup_menu.Append(ID_DELETE, _('Delete'))
        self.popup_menu.AppendSeparator()
        self.popup_menu.Append(ID_REFRESH, _('Refresh'))
        self.Bind(wx.EVT_MENU, self.OnContextMenu, id=ID_NEW_DIRECTORY)
        self.Bind(wx.EVT_MENU, self.OnContextMenu, id=ID_RENAME)
        self.Bind(wx.EVT_MENU, self.OnContextMenu, id=ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnContextMenu, id=ID_REFRESH)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_NEW_DIRECTORY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_RENAME)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_DELETE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_REFRESH)

    def OnItemCollapsing(self, event):
        event.Veto()

    def OnItemActivate(self, event):
        id = event.GetItem()
        if id == self.rootid:
            parent = os.path.dirname(self.rootdir)
            self.SetRootDir(parent)
        else:
            dir = self.GetItemText(id)
            path = os.path.join(self.rootdir, dir)
            if os.path.isdir(path):
                self.SetRootDir(path)
            else:
                evt = LoadFileEvent(filename=path, id=self.GetId())
                wx.PostEvent(self, evt)
        return

    def OnSize(self, event):
        if self.rootid.IsOk():
            self.SetItemText(self.rootid, self.GetDisplayName(self.rootdir))
        event.Skip()

    def OnRightDown(self, event):
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)
        if item:
            self.SelectItem(item)
        return

    def OnRightUp(self, event):
        self.PopupMenu(self.popup_menu)

    def OnContextMenu(self, event):
        id = event.GetId()
        item = self.GetSelection()
        if id == ID_NEW_DIRECTORY:
            newpath = self.NewDirectory()
            if newpath:
                self.AppendItem(self.rootid, newpath, 0)
        elif id == ID_RENAME:
            path = self.GetItemText(item)
            newpath = self.RenamePath(path)
            if newpath:
                self.SetItemText(item, newpath)
        elif id == ID_DELETE:
            path = self.GetItemText(item)
            if self.DeletePath(path):
                self.Delete(item)
        elif id == ID_REFRESH:
            self.SetRootDir(self.rootdir, refresh=True)

    def OnUpdateUI(self, event):
        id = event.GetId()
        point = self.ScreenToClient(wx.GetMousePosition())
        item = self.HitTest(point)[0]
        if id == ID_NEW_DIRECTORY:
            event.Enable(True)
        elif id == ID_RENAME:
            event.Enable(item.IsOk())
        elif id == ID_DELETE:
            event.Enable(item.IsOk())
        elif id == ID_REFRESH:
            event.Enable(True)

    def OnSetRoot(self, event):
        path = event.path
        refresh = event.refresh
        self.SetRootDir(path, refresh)

    def SetRootDir(self, path=None, refresh=False):
        """ set exporer root directory """
        if not path:
            path = os.getcwd()
        if not refresh and path == self.rootdir:
            return
        self.DeleteAllItems()
        self.rootdir = path
        os.chdir(path)
        self.rootid = self.AddRoot(self.GetDisplayName(self.rootdir), 1)
        dirs = sorted(os.listdir(self.rootdir))
        for dir in dirs:
            path = os.path.join(self.rootdir, dir)
            if os.path.isdir(path):
                self.AppendItem(self.rootid, dir, 0)
            else:
                self.AppendItem(self.rootid, dir, 2)
        self.Expand(self.rootid)

    def GetDisplayName(self, name):
        """ directory display name """
        client_width = self.GetClientSizeTuple()[0] - 32
        char_width = self.GetCharWidth()
        disp_char_num = client_width / char_width - 1
        if (len(name) - 3) > disp_char_num:
            display_name = '<<<'
            display_name += name[-disp_char_num + 3:]
        else:
            display_name = name
        return display_name

    def DeletePath(self, path):
        if os.path.exists(path):
            answer = wx.MessageBox(_('Do you want to delete "%s"?')% path,
                                   _('Delete'),
                                   wx.YES_NO|wx.ICON_QUESTION,
                                   self.GetParent())
            if answer == wx.YES:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    return True
                except Exception as err:
                    wx.MessageBox(err, _('Error'), wx.YES|wx.ICON_INFORMATION, self)
        return False

    def RenamePath(self, path):
        txtdlg = wx.TextEntryDialog(self.GetParent(),
                                    _('Please input name:'),
                                    _('Rename'),
                                    path,
                                    wx.OK|wx.CANCEL|wx.CENTER)
        if txtdlg.ShowModal() == wx.ID_OK:
            newpath = txtdlg.GetValue()
            if os.path.exists(newpath):
                wx.MessageBox(_('File "%s" has existed!')% newpath,
                              _('Exists'),
                              wx.OK)
                return
            os.rename(path, newpath)
            return txtdlg.GetValue()
        return

    def NewDirectory(self):
        txtdlg = wx.TextEntryDialog(self.GetParent(),
                                    _('Please input name:'),
                                    _('New directory'),
                                    '',
                                    wx.OK|wx.CANCEL|wx.CENTER)
        if txtdlg.ShowModal() == wx.ID_OK:
            newpath = txtdlg.GetValue()
            if os.path.exists(newpath):
                wx.MessageBox(_('File "%s" has existed!')% newpath,
                              _('Exists'),
                              wx.OK)
                return
            os.mkdir(newpath)
            return newpath
        return
