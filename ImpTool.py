import sys

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.cmds as cmds
import maya.OpenMayaUI as omUi



def get_python_version():
    return sys.version_info.major

def maya_main_window():
        
    main_window_ptr = omUi.MQtUtil.mainWindow()
    #chech for the python version so we can use the correct Cast
    if get_python_version() >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class ImpToolsDialog(QtWidgets.QDialog):
    
    FILE_FILTERS = 'Maya (*.ma *.mb);; Maya ASCII (*.ma);; Maya Binary (*.mb);; All Files (*.*)'
    selected_filter = 'Maya (*.ma *.mb)'
    
    
    #### for release
    dialog_instance = None
    @classmethod
    def show_dialog(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = ImpToolsDialog()
            
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()
    
    def __init__(self, parent=maya_main_window()):
        print('started')
        super(ImpToolsDialog, self).__init__(parent)
        
        self.setWindowTitle('Impprt/Link/Open Tools')
        self.setMinimumSize(500,100)
        
        self.creat_widgets()
        self.creat_layouts()
        self.creat_connections()
        
        
    def creat_widgets(self):
        #file path widgets
        self.file_path_le = QtWidgets.QLineEdit()
        self.file_path_btn = QtWidgets.QPushButton()
        self.file_path_btn.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.file_path_btn.setToolTip('Open File')
        
        #radio button widgets
        self.open_rb = QtWidgets.QRadioButton('Open')
        self.open_rb.setChecked(True)
        self.import_rb = QtWidgets.QRadioButton('import')
        self.refrence_rb = QtWidgets.QRadioButton('Refrence')
        
        #force widget
        self.force_cb = QtWidgets.QCheckBox('Force')
        
        #Ok and cancel button widgets
        self.ok_btn = QtWidgets.QPushButton('OK')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')
        
        
        
    def creat_layouts(self):
        self.file_path_layout = QtWidgets.QHBoxLayout()
        self.file_path_layout.addWidget(self.file_path_le)
        self.file_path_layout.addWidget(self.file_path_btn)
        
        self.radio_btn_layout = QtWidgets.QHBoxLayout()
        self.radio_btn_layout.addWidget(self.open_rb)
        self.radio_btn_layout.addWidget(self.import_rb)
        self.radio_btn_layout.addWidget(self.refrence_rb)
        
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_btn)
        self.button_layout.addWidget(self.cancel_btn)
        
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow('File: ', self.file_path_layout)
        self.form_layout.addRow('', self.radio_btn_layout)
        self.form_layout.addRow('',self.force_cb)
        self.form_layout.addRow('',self.button_layout)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.form_layout)
        
        
    def creat_connections(self):
        
        self.file_path_btn.clicked.connect(self.open_file_select_dialog)
        
        self.open_rb.toggled.connect(self.toggel_force_visibility)
        
        self.ok_btn.clicked.connect(self.load_file)
        self.cancel_btn.clicked.connect(self.close)
        
        
    def open_file_select_dialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self,'Selecet file', '', self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.file_path_le.setText(file_path)
        
        
        
    def toggel_force_visibility(self, checked):
        self.force_cb.setVisible(checked)
        
    def load_file(self):
        file_path = self.file_path_le.text()
        
        if not file_path:
            om.MGlobal.displayError('No File Path')
            return
        
        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists():
            om.MGlobal.displayError('File dose not exists {0}'.format(file_path))
            return
        
        if self.open_rb.isChecked():
            self.open_file(file_path)
        elif self.import_rb.isChecked():
            self.import_file(file_path)
        else:
            self.refrence_file(file_path)
            
    
    def open_file(self, file_path):
        force = self.force_cb.isChecked()
        
        #Ask user if they want to discard changes in current scene
        if not force and cmds.file(q=True, modified=True):
            res = QtWidgets.QMessageBox.question(self, 'Modified', 'Current Scene has been change wanna continue?')
            if res == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True
            else:
                return
            
        
        cmds.file(file_path, open=True, ignoreVersion=True, force=force)
    
    def import_file(self, file_path):
        cmds.file(file_path, i=True, ignoreVersion=True)
    
    def refrence_file(self, file_path):
        cmds.file(file_path, reference=True, ignoreVersion=True)
            
        

if __name__ == '__main__':
    
    try:
        ImpTool_dialog.close() #pylint: disable=E0601
        ImpTool_dialog.deleteLater()
    except:
        pass
    
    ImpTool_dialog = ImpToolsDialog()
    ImpTool_dialog.show()
    
        