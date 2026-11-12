from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QComboBox, QInputDialog, QMessageBox

from packages.Startup.Options import Options, save_options
from packages.Tabs.GlobalSetting import GlobalSetting

PLACEHOLDER_ITEM = "placeholder"
PRESET_ITEM = "preset"
SAVE_ITEM = "save"
DELETE_ITEM = "delete"


class TrackPresetComboBox(QComboBox):
    """
    Dropdown next to the audio/subtitle tab selector.
    Lets the user apply a saved track preset to the current tab, save the current tab settings as preset
    or delete a preset. Presets are stored in Options.<track_type>_Track_Presets.
    """
    apply_preset_signal = Signal(dict)

    def __init__(self, track_type, get_current_settings):
        super().__init__()
        self.track_type = track_type  # "Audio" or "Subtitle"
        self.get_current_settings = get_current_settings
        self.hint_when_enabled = ""
        self.setMinimumWidth(170)
        # placeholder + presets + separator + save/delete: show ~20 presets before a scrollbar appears
        self.setMaxVisibleItems(24)
        self.view().setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.setToolTip(f"<nobr>Apply a saved {track_type.lower()} preset to the current {track_type.lower()} tab"
                        f"<br>or save the current settings as new preset<br>(all settings except delay and source)")
        self.setToolTipDuration(12000)
        self.refresh_items()
        self.activated.connect(self.item_activated)

    def get_presets(self):
        return getattr(Options, self.track_type + "_Track_Presets")

    def set_presets(self, presets):
        setattr(Options, self.track_type + "_Track_Presets", presets)
        save_options()

    def get_presets_names(self):
        return [preset.get("name", "") for preset in self.get_presets()]

    def refresh_items(self):
        self.blockSignals(True)
        self.clear()
        self.addItem(f"{self.track_type} Presets", (PLACEHOLDER_ITEM, -1))
        for preset_index, preset_name in enumerate(self.get_presets_names()):
            self.addItem(preset_name, (PRESET_ITEM, preset_index))
            self.setItemData(self.count() - 1, "Apply preset: " + preset_name, Qt.ItemDataRole.ToolTipRole)
        self.insertSeparator(self.count())
        self.addItem("Save current as preset...", (SAVE_ITEM, -1))
        if len(self.get_presets()) > 0:
            self.addItem("Delete preset...", (DELETE_ITEM, -1))
        self.setCurrentIndex(0)
        self.update_popup_width()
        self.blockSignals(False)

    def update_popup_width(self):
        # popup as wide as the longest preset name, so names are never cut off
        metrics = self.view().fontMetrics()
        longest_text_width = max([metrics.horizontalAdvance(self.itemText(i)) for i in range(self.count())] + [0])
        scrollbar_width = self.view().verticalScrollBar().sizeHint().width()
        self.view().setMinimumWidth(longest_text_width + scrollbar_width + 30)

    def item_activated(self, index):
        item_data = self.itemData(index)
        if item_data is None:
            self.setCurrentIndex(0)
            return
        item_type, preset_index = item_data
        if item_type == PRESET_ITEM:
            self.apply_preset_signal.emit(dict(self.get_presets()[preset_index]))
        elif item_type == SAVE_ITEM:
            self.save_current_as_preset()
        elif item_type == DELETE_ITEM:
            self.delete_preset()
        self.refresh_items()

    def save_current_as_preset(self):
        names = self.get_presets_names()
        default_name = f"{self.track_type} Preset #{len(names) + 1}"
        name, ok = QInputDialog.getText(self.window(), "Save Preset", "Preset name:", text=default_name)
        name = name.strip()
        if not ok or name == "":
            return
        new_preset = dict(self.get_current_settings())
        new_preset["name"] = name
        presets = list(self.get_presets())
        if name in names:
            answer = QMessageBox.question(self.window(), "Overwrite Preset",
                                          f"Preset \"{name}\" already exists.\nOverwrite it?")
            if answer != QMessageBox.StandardButton.Yes:
                return
            presets[names.index(name)] = new_preset
        else:
            presets.append(new_preset)
        self.set_presets(presets)

    def delete_preset(self):
        names = self.get_presets_names()
        if len(names) == 0:
            return
        name, ok = QInputDialog.getItem(self.window(), "Delete Preset", "Preset to delete:", names, 0, False)
        if not ok or name not in names:
            return
        presets = list(self.get_presets())
        del presets[names.index(name)]
        self.set_presets(presets)

    def setEnabled(self, new_state: bool):
        super().setEnabled(new_state)
        if not new_state and not GlobalSetting.JOB_QUEUE_EMPTY:
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
