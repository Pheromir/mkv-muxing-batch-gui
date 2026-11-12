from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QCheckBox

from packages.Startup.InitializeScreenResolution import screen_size
from packages.Startup.PreDefined import AllVideosLanguages
from packages.Tabs.GlobalSetting import GlobalSetting

VIDEO_KEEP_OLD_LANGUAGE = "[Old]"
VIDEO_DEFAULT_LANGUAGE = "Undetermined"


class _DisableTooltipMixin:
    """same tooltip handling as the other widgets while the job queue is locked"""

    def setEnabled(self, new_state: bool):
        super().setEnabled(new_state)
        self._update_disable_tooltip(not new_state)

    def setDisabled(self, new_state: bool):
        super().setDisabled(new_state)
        self._update_disable_tooltip(new_state)

    def _update_disable_tooltip(self, disabled):
        if disabled and not GlobalSetting.JOB_QUEUE_EMPTY:
            if self.hint_when_enabled != "":
                self.setToolTip("<nobr>" + self.hint_when_enabled + "<br>" + GlobalSetting.DISABLE_TOOLTIP)
            else:
                self.setToolTip("<nobr>" + GlobalSetting.DISABLE_TOOLTIP)
        else:
            self.setToolTip(self.hint_when_enabled)

    def setToolTip(self, new_tool_tip: str):
        if self.isEnabled() or GlobalSetting.JOB_QUEUE_EMPTY:
            self.hint_when_enabled = new_tool_tip
        super().setToolTip(new_tool_tip)


class VideoTrackNameLineEdit(_DisableTooltipMixin, QLineEdit):
    def __init__(self):
        super().__init__()
        self.hint_when_enabled = ""
        self.setPlaceholderText("No Track Name")
        self.setMinimumWidth(screen_size.width() // 12)
        self.setClearButtonEnabled(True)
        self.setToolTip("<nobr>Track name of the video track(s)<br>Leave empty to remove the old track name")
        self.textChanged.connect(self.change_global_video_track_name)
        GlobalSetting.VIDEO_TRACK_NAME = ""

    def change_global_video_track_name(self):
        GlobalSetting.VIDEO_TRACK_NAME = self.text()


class VideoTrackNameKeepOldCheckBox(_DisableTooltipMixin, QCheckBox):
    def __init__(self):
        super().__init__()
        self.hint_when_enabled = ""
        self.setText("Keep Old")
        self.setToolTip("<nobr>Keep the track name of the source video track(s)")
        self.stateChanged.connect(self.change_global_video_track_name_keep_old)
        GlobalSetting.VIDEO_TRACK_NAME_KEEP_OLD = False

    def change_global_video_track_name_keep_old(self):
        GlobalSetting.VIDEO_TRACK_NAME_KEEP_OLD = self.checkState() == Qt.CheckState.Checked


class VideoLanguageComboBox(_DisableTooltipMixin, QComboBox):
    def __init__(self):
        super().__init__()
        self.hint_when_enabled = ""
        self.setMinimumWidth(screen_size.width() // 14)
        self.addItem(VIDEO_KEEP_OLD_LANGUAGE)
        self.addItems(AllVideosLanguages)
        for i in range(self.count()):
            self.setItemData(i, self.itemText(i), Qt.ItemDataRole.ToolTipRole)
        self.setMaxVisibleItems(8)
        self.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.setCurrentText(VIDEO_DEFAULT_LANGUAGE)
        GlobalSetting.VIDEO_LANGUAGE = self.currentText()
        self.setToolTip("<nobr>Language of the video track(s)<br><b>[Old]</b> keeps the language of the source")
        self.currentTextChanged.connect(self.change_global_video_language)

    def change_global_video_language(self):
        GlobalSetting.VIDEO_LANGUAGE = self.currentText()
