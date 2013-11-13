=========
RSTEditor
=========
RSTEditor is a editor for ReStructedText. It support preview with html.

.. tip::

    由于无法修复中文输入Bug，请使用本软件的QT版本，rsteditor-qt
    
    
Requirement
===========
Install them on all platform:

+ docutils
+ wxPython
+ Pygments

For Window:

.. tip::

    Do not support scroll synchronize on Window.

Install it on Window:

+ comtypes

For Linux:
Install them:

+ pygtk
+ pywebkitgtk

Template
========
template::

    skeleton.rst

Bug
====
使用中文输入法时，如果中间使用删除，回车，光标等键时，不能继续输入中文，需要重新切换输入法才能再次输入，英文不受影响。wxStyledTextCtrl控件问题，无法解决！

