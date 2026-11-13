from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QCheckBox

from packages.Startup.Options import Options, save_options
from packages.Tabs.GlobalSetting import GlobalSetting


class MkvTitleLineEdit(QLineEdit):
    """Title of the output MKV file (segment title), empty keeps the title of the source video"""

    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Keep Old Title")
        self.setClearButtonEnabled(True)
        self.setToolTip("<nobr>Title of the output MKV file<br>Leave empty to keep the title of the source video")
        self.setToolTipDuration(12000)
        self.textChanged.connect(self.change_global_mkv_title)
        GlobalSetting.MUX_SETTING_MKV_TITLE = ""

    def change_global_mkv_title(self):
        GlobalSetting.MUX_SETTING_MKV_TITLE = self.text()


class MkvTitleRemoveCheckBox(QCheckBox):
    """Removes the title of the output MKV file, the choice is remembered across restarts"""

    def __init__(self):
        super().__init__()
        self.setText("Remove Title")
        self.setToolTip("<nobr>Remove the title of the output MKV file completely<br>"
                        "This choice is remembered for the next start")
        self.setToolTipDuration(12000)
        self.setChecked(bool(Options.Mux_Remove_Title))
        GlobalSetting.MUX_SETTING_MKV_REMOVE_TITLE = self.isChecked()
        self.stateChanged.connect(self.change_global_mkv_remove_title)

    def change_global_mkv_remove_title(self):
        GlobalSetting.MUX_SETTING_MKV_REMOVE_TITLE = self.checkState() == Qt.CheckState.Checked
        Options.Mux_Remove_Title = GlobalSetting.MUX_SETTING_MKV_REMOVE_TITLE
        save_options()
