import os
from calibre.gui2.actions import InterfaceAction
from PyQt5.Qt import  QDialog, QListWidgetItem 
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox, QLabel, QListWidget, QApplication
from calibre.utils.config import prefs

class Ui_LibraryDialog(object):
    def setupUi(self, LibraryDialog):
        LibraryDialog.setObjectName("LibraryDialog")
        LibraryDialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(LibraryDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QLabel(LibraryDialog)
        self.label.setGeometry(QtCore.QRect(70, 30, 211, 17))
        self.label.setObjectName("label")
        self.listWidget = QListWidget(LibraryDialog)
        self.listWidget.setGeometry(QtCore.QRect(70, 60, 181, 151))
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(LibraryDialog)
        self.buttonBox.accepted.connect(LibraryDialog.accept)
        self.buttonBox.rejected.connect(LibraryDialog.reject)

    def retranslateUi(self, LibraryDialog):
        LibraryDialog.setWindowTitle(QApplication.translate("LibraryDialog", "Library Switcher", None ))
        self.label.setText(QApplication.translate("LibraryDialog", "Choose a library:", None))


class SwitchLibraryDialog(QDialog,Ui_LibraryDialog):
    
    def __init__(self,window,locations):
        QDialog.__init__(self,window)
        Ui_LibraryDialog.__init__(self)
        self.locations=locations
        self.setupUi(self)
        for name, location in locations:
            self.listWidget.addItem(QListWidgetItem(name))
        self.location=None
        self.listWidget.setCurrentRow(0)


    def accept(self):
        print "OK!"
        self.location = self.locations[self.listWidget.currentRow()][1]
        return QDialog.accept(self)


class QuickSwitchLibraryPlugin(InterfaceAction):
    name = 'Quick Switch Library Plugin'
    action_spec = ('Quick Switch Library', None, 
                   'Run Quick Switch Library', 'Ctrl+Shift+b')

    def genesis(self):
        print 'in QuickSwitchLibraryPlugin genesis method'
        self.qaction.triggered.connect(self.dialog)
        

    def dialog(self):
        print 'triggered dialog in QuickSwitchLibraryPlugin'
        from calibre.gui2.actions.choose_library import LibraryUsageStats
        from calibre.gui2 import gprefs
        stats=LibraryUsageStats()
        db = self.gui.library_view.model().db
        locations = list(stats.locations(db))
        print locations
        for name, loc in locations:
            print "%s in %s" % (name,loc)
        dialog = SwitchLibraryDialog(self.gui,locations)
        dialog.setModal(True)
        dialog.show()
        if dialog.exec_() != dialog.Accepted:
            return
        else:
            self.switch_requested(dialog.location)
            print dialog.location

    def change_library_allowed(self):
        if os.environ.get('CALIBRE_OVERRIDE_DATABASE_PATH', None):
            warning_dialog(self.gui, _('Not allowed'),
                    _('You cannot change libraries while using the environment'
                        ' variable CALIBRE_OVERRIDE_DATABASE_PATH.'), show=True)
            return False
        if self.gui.job_manager.has_jobs():
            warning_dialog(self.gui, _('Not allowed'),
                    _('You cannot change libraries while jobs'
                        ' are running.'), show=True)
            return False

        return True


    def switch_requested(self, location):
        if not self.change_library_allowed():
            return
        loc = location.replace('/', os.sep)
        exists = self.gui.library_view.model().db.exists_at(loc)
        if not exists:
            warning_dialog(self.gui, _('No library found'),
                    _('No existing calibre library was found at %s.'
                    ' It will be removed from the list of known'
                    ' libraries.')%loc, show=True)
            self.stats.remove(location)
            self.build_menus()
            self.gui.iactions['Copy To Library'].build_menus()
            return

        prefs['library_path'] = loc
        self.gui.library_moved(loc)

