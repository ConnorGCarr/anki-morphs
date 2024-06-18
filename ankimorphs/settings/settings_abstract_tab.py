from __future__ import annotations

import pprint
from abc import ABC, abstractmethod

from aqt.qt import (  # pylint:disable=no-name-in-module
    QCheckBox,
    QDialog,
    QKeySequenceEdit,
    QLineEdit,
    QRadioButton,
    QSpinBox,
)

from .. import message_box_utils
from ..ankimorphs_config import AnkiMorphsConfig
from ..ui.settings_dialog_ui import Ui_SettingsDialog


class AbstractSettingsTab(ABC):  # pylint:disable=too-many-instance-attributes
    def __init__(
        self,
        parent: QDialog,
        ui: Ui_SettingsDialog,
        config: AnkiMorphsConfig,
        default_config: AnkiMorphsConfig,
    ):
        self._parent = parent
        self.ui = ui
        self._config = config
        self._default_config = default_config

        self._raw_config_key_to_radio_button: dict[str, QRadioButton] = {}
        self._raw_config_key_to_check_box: dict[str, QCheckBox] = {}
        self._raw_config_key_to_spin_box: dict[str, QSpinBox] = {}
        self._raw_config_key_to_line_edit: dict[str, QLineEdit] = {}
        self._raw_config_key_to_key_sequence: dict[str, QKeySequenceEdit] = {}

        self._previous_state: dict[str, str | int | bool | object] | None = None

        # subclasses should run these in their __init__:
        # 1. self.populate()
        # 2. self.setup_buttons()
        # 3. self.update_previous_state()

    @abstractmethod
    def setup_buttons(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_confirmation_text(self) -> str:
        raise NotImplementedError

    def populate(self) -> None:
        for (
            config_attribute,
            radio_button,
        ) in self._raw_config_key_to_radio_button.items():
            is_checked = getattr(self._config, config_attribute)
            radio_button.setChecked(is_checked)

        for config_attribute, checkbox in self._raw_config_key_to_check_box.items():
            is_checked = getattr(self._config, config_attribute)
            checkbox.setChecked(is_checked)

        for config_attribute, spin_box in self._raw_config_key_to_spin_box.items():
            value = getattr(self._config, config_attribute)
            spin_box.setValue(value)

        for config_attribute, line_edit in self._raw_config_key_to_line_edit.items():
            tag = getattr(self._config, config_attribute)
            line_edit.setText(tag)

        for (
            config_attribute,
            key_sequence_edit,
        ) in self._raw_config_key_to_key_sequence.items():
            key_sequence = getattr(self._config, config_attribute)
            key_sequence_edit.setKeySequence(key_sequence)

    def restore_defaults(self, skip_confirmation: bool = False) -> None:
        if not skip_confirmation:
            title = "Confirmation"
            text = self.get_confirmation_text()
            confirmed = message_box_utils.warning_dialog(
                title, text, parent=self._parent
            )

            if not confirmed:
                return

        for (
            config_attribute,
            radio_button,
        ) in self._raw_config_key_to_radio_button.items():
            is_checked = getattr(self._default_config, config_attribute)
            radio_button.setChecked(is_checked)

        for config_attribute, spin_box in self._raw_config_key_to_spin_box.items():
            value = getattr(self._default_config, config_attribute)
            spin_box.setValue(value)

        for config_attribute, checkbox in self._raw_config_key_to_check_box.items():
            is_checked = getattr(self._default_config, config_attribute)
            checkbox.setChecked(is_checked)

        for config_attribute, line_edit in self._raw_config_key_to_line_edit.items():
            tag = getattr(self._default_config, config_attribute)
            line_edit.setText(tag)

        for (
            config_attribute,
            key_sequence_edit,
        ) in self._raw_config_key_to_key_sequence.items():
            key_sequence = getattr(self._default_config, config_attribute)
            key_sequence_edit.setKeySequence(key_sequence)

    def restore_to_config_state(self) -> None:
        assert self._previous_state is not None

        for config_key, radio_button in self._raw_config_key_to_radio_button.items():
            previous_check_state = self._previous_state[config_key]
            assert isinstance(previous_check_state, bool)
            radio_button.setChecked(previous_check_state)

        for config_key, spin_box in self._raw_config_key_to_spin_box.items():
            previous_value = self._previous_state[config_key]
            assert isinstance(previous_value, int)
            spin_box.setValue(previous_value)

        for config_key, checkbox in self._raw_config_key_to_check_box.items():
            previous_check_state = self._previous_state[config_key]
            assert isinstance(previous_check_state, bool)
            checkbox.setChecked(previous_check_state)

        for config_key, line_edit in self._raw_config_key_to_line_edit.items():
            previous_tag = self._previous_state[config_key]
            assert isinstance(previous_tag, str)
            line_edit.setText(previous_tag)

        for (
            config_key,
            key_sequence_edit,
        ) in self._raw_config_key_to_key_sequence.items():
            previous_key_sequence = self._previous_state[config_key]
            assert isinstance(previous_key_sequence, str)
            key_sequence_edit.setKeySequence(previous_key_sequence)

    def settings_to_dict(self) -> dict[str, str | int | bool | object]:
        radio_button_settings = {
            config_key: radio_button.isChecked()
            for config_key, radio_button in self._raw_config_key_to_radio_button.items()
        }
        spin_box_settings = {
            config_key: spin_box.value()
            for config_key, spin_box in self._raw_config_key_to_spin_box.items()
        }
        check_box_settings = {
            config_key: checkbox.isChecked()
            for config_key, checkbox in self._raw_config_key_to_check_box.items()
        }
        line_edit_settings = {
            config_key: line_edit.text()
            for config_key, line_edit in self._raw_config_key_to_line_edit.items()
        }
        key_sequence_settings = {
            config_key: key_sequence.keySequence().toString()
            for config_key, key_sequence in self._raw_config_key_to_key_sequence.items()
        }

        settings_dict: dict[str, str | int | bool | object] = {}
        settings_dict.update(radio_button_settings)
        settings_dict.update(spin_box_settings)
        settings_dict.update(check_box_settings)
        settings_dict.update(line_edit_settings)
        settings_dict.update(key_sequence_settings)

        return settings_dict

    def update_previous_state(self) -> None:
        self._previous_state = self.settings_to_dict()

    def contains_unsaved_changes(self) -> bool:
        assert self._previous_state is not None

        current_state = self.settings_to_dict()
        print("current_state")
        pprint.pp(current_state)

        print("_initial_state")
        pprint.pp(self._previous_state)

        if current_state != self._previous_state:
            print("NOT the same")
            return True

        print("the same")
        return False
