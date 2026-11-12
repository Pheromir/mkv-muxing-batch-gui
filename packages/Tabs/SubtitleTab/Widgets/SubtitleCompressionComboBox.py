from PySide6.QtWidgets import QComboBox

from packages.Startup.Options import Options, save_options
from packages.Startup.PreDefined import AllSubtitleCompressions
from packages.Tabs.GlobalSetting import GlobalSetting


class SubtitleCompressionComboBox(QComboBox):
    def __init__(self, tab_index):
        super().__init__()
        self.tab_index = tab_index
        self.hint_when_enabled = ""
        self.addItems(AllSubtitleCompressions)
        if Options.Subtitle_Compression not in AllSubtitleCompressions:
            Options.Subtitle_Compression = AllSubtitleCompressions[0]
        self.setCurrentText(Options.Subtitle_Compression)
        GlobalSetting.SUBTITLE_COMPRESSION[self.tab_index] = self.currentText()
        self.setToolTip("<nobr>Compression of the new subtitle track<br>"
                        "<b>Default</b>: let mkvmerge decide (zlib for some formats, e.g. VobSub/PGS)<br>"
                        "<b>None</b>: store the subtitle uncompressed<br>"
                        "<b>Zlib</b>: always compress with zlib")
        self.setToolTipDuration(12000)
        self.currentTextChanged.connect(self.change_global_subtitle_compression)

    def change_global_subtitle_compression(self):
        GlobalSetting.SUBTITLE_COMPRESSION[self.tab_index] = self.currentText()
        # remember the last used choice as default for new tabs / next start
        Options.Subtitle_Compression = self.currentText()
        save_options()

    def reset_to_default(self):
        self.setCurrentText(Options.Subtitle_Compression)
        GlobalSetting.SUBTITLE_COMPRESSION[self.tab_index] = self.currentText()

    def setEnabled(self, new_state: bool):
        super().setEnabled(new_state)
        if not new_state and not GlobalSetting.JOB_QUEUE_EMPTY:
            if self.hint_when_enabled != "":
                self.setToolTip("<nobr>" + self.hint_when_enabled + "<br>" + GlobalSetting.DISABLE_TOOLTIP)
            else:
                self.setToolTip("<nobr>" + GlobalSetting.DISABLE_TOOLTIP)
        else:
            self.setToolTip(self.hint_when_enabled)

    def setDisabled(self, new_state: bool):
        super().setDisabled(new_state)
        if new_state and not GlobalSetting.JOB_QUEUE_EMPTY:
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
