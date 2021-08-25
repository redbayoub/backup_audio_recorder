from ui_conf_controller import UiConfController
from constants import Constants
import validators
from backup_audio_recorder import BackupAudioRecorder
import sounddevice
import dialogs
import os
import json
import tkinter as tk
import pygubu

# this is added to fix issues when using Pyinstaller command
from pygubu.builder import tkstdwidgets
from pygubu.builder import ttkstdwidgets

PRIMARY_COLOR = "#1492e6"


PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "gui.ui")


class GuiApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object("mainwindow", master)

        builder.connect_callbacks(self)

        self.conf = UiConfController()

        # if output directory doesn't exists set to default
        if not os.path.isdir(self.conf.get_conf("output_directory")):
            self.conf.set_conf(
                "output_directory", self.conf.get_default_conf("output_directory")
            )

        # setup duration entries callbacks
        self.builder.get_variable("dur_days").trace_add(
            "write", self.on_duration_change
        )
        self.builder.get_variable("dur_hours").trace_add(
            "write", self.on_duration_change
        )
        self.builder.get_variable("dur_minutes").trace_add(
            "write", self.on_duration_change
        )
        self.builder.get_variable("dur_seconds").trace_add(
            "write", self.on_duration_change
        )

        # init entries
        self.__set_entry("location_entry", self.conf.get_conf("output_directory"))
        self.__set_entry("days_dur_entry", self.conf.get_conf("dur_days"))
        self.__set_entry("hours_dur_entry", self.conf.get_conf("dur_hours"))
        self.__set_entry("minutes_dur_entry", self.conf.get_conf("dur_minutes"))
        self.__set_entry("seconds_dur_entry", self.conf.get_conf("dur_seconds"))
        self.builder.get_variable("startup_recording_state").set(
            self.conf.get_conf("startup_recording")
        )

        self.init_devices_menu()

        self.recorder = BackupAudioRecorder(
            output_directory=self.conf.get_conf("output_directory"),
            listening_finished_callback=self.listen,
            exporting_finished_callback=self.export,
            input_device=self.current_input_device,
            output_device=self.current_output_device,
        )

        if self.builder.get_variable("startup_recording_state").get():
            self.record()

    def init_devices_menu(self):
        default_input_device = sounddevice.query_devices(kind="input")["name"]
        default_output_device = sounddevice.query_devices(kind="output")["name"]
        input_devices = [
            device["name"]
            for device in sounddevice.query_devices()
            if device["max_input_channels"] > 0
        ]
        output_devices = [
            device["name"]
            for device in sounddevice.query_devices()
            if device["max_output_channels"] > 0
        ]

        self.current_input_device = self.conf.get_conf("input_device")
        self.current_output_device = self.conf.get_conf("output_device")

        self.builder.get_object("input_device_menu").config(
            values=[f"Default: {default_input_device}"] + input_devices
        )
        self.builder.get_object("input_device_menu").current(
            0
            if not self.current_input_device
            else input_devices.index(self.current_input_device) + 1
        )
        self.builder.get_object("input_device_menu").bind(
            "<<ComboboxSelected>>", self.on_input_device_selected
        )

        self.builder.get_object("output_device_menu").config(
            values=[f"Default: {default_output_device}"] + output_devices
        )
        self.builder.get_object("output_device_menu").current(
            0
            if not self.current_output_device
            else output_devices.index(self.current_output_device) + 1
        )
        self.builder.get_object("output_device_menu").bind(
            "<<ComboboxSelected>>", self.on_output_device_selected
        )

    def on_duration_change(self, _, __, ___):
        duration = self.__get_duration()
        filesize = BackupAudioRecorder.get_estimated_filesize(duration)
        self.builder.get_variable("estimated_filesize").set(filesize)

    def browse(self):
        output_dir_path = dialogs.ask_folder(
            initialdir=self.conf.get_conf("output_directory")
        )
        if output_dir_path:
            self.__set_entry("location_entry", output_dir_path)
            self.recorder.set_output_directory(output_dir_path)
            self.conf.set_conf(
                "output_directory",
                output_dir_path,
            )

    def is_int(self, value):
        return validators.is_int(value)

    def listen(self):
        listen_btn = self.builder.get_object("listen_btn")
        if self.recorder.is_listening:
            self.recorder.stop_listening()
            listen_btn.config(text="Listen")
        else:
            self.recorder.start_listening()
            listen_btn.config(text="Listening ...")

    def record(self):
        record_btn = self.builder.get_object("record_btn")
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            record_btn.config(text="Record", background=PRIMARY_COLOR)
        else:
            duration = self.__get_duration()
            if duration == 0:
                return
            self.__save_duration()
            self.recorder.start_recording(duration)
            record_btn.config(text="Recording ...", background="#ff0000")

    def export(self):
        export_btn = self.builder.get_object("export_btn")
        if self.recorder.is_exporting:
            self.recorder.stop_exporting()
            export_btn.config(text="Export")
        else:
            export_file_path = dialogs.ask_file_save_location("wav")
            if not export_file_path:
                return

            self.recorder.start_exporting(export_file_path)
            export_btn.config(text="Exporting ...")

    def startup_recording_callback(self):
        self.conf.set_conf(
            "startup_recording",
            self.builder.get_variable("startup_recording_state").get(),
        )

    def on_input_device_selected(self, event):
        selected_input_device = self.builder.get_object("input_device_menu").get()
        if selected_input_device == self.current_input_device:
            return

        if selected_input_device.lower().startswith("default"):
            self.current_input_device = None
        else:
            self.current_input_device = selected_input_device
        self.recorder.set_input_device(self.current_input_device)
        self.conf.set_conf(
            "input_device",
            self.current_input_device,
        )

    def on_output_device_selected(self, event):
        selected_output_device = self.builder.get_object("output_device_menu").get()
        if selected_output_device == self.current_output_device:
            return

        if selected_output_device.lower().startswith("default"):
            self.current_output_device = None
        else:
            self.current_output_device = selected_output_device
        self.recorder.set_output_device(self.current_output_device)
        self.conf.set_conf(
            "output_device",
            self.current_input_device,
        )

    def run(self):
        self.mainwindow.mainloop()

    def __save_duration(self):
        duration = self.get_duration_fields()

        self.conf.set_conf(
            "dur_seconds",
            duration["dur_seconds"],
            auto_save=False,
        )
        self.conf.set_conf(
            "dur_minutes",
            duration["dur_minutes"],
            auto_save=False,
        )
        self.conf.set_conf(
            "dur_hours",
            duration["dur_hours"],
            auto_save=False,
        )
        self.conf.set_conf(
            "dur_days",
            duration["dur_days"],
            auto_save=False,
        )

        self.conf.save_conf()

    def __set_entry(self, entry_id, value):
        entry = self.builder.get_object(entry_id)
        initial_entry_state = entry["state"]
        if not initial_entry_state == "normal":
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        if not initial_entry_state == "normal":
            entry.configure(state=initial_entry_state)

    def get_duration_fields(self):
        dur_seconds = self.builder.get_variable("dur_seconds").get()
        dur_minutes = self.builder.get_variable("dur_minutes").get()
        dur_hours = self.builder.get_variable("dur_hours").get()
        dur_days = self.builder.get_variable("dur_days").get()

        dur_seconds = 0 if dur_seconds == "" else int(dur_seconds)
        dur_minutes = 0 if dur_minutes == "" else int(dur_minutes)
        dur_hours = 0 if dur_hours == "" else int(dur_hours)
        dur_days = 0 if dur_days == "" else int(dur_days)
        return {
            "dur_seconds": dur_seconds,
            "dur_minutes": dur_minutes,
            "dur_hours": dur_hours,
            "dur_days": dur_days,
        }

    def __get_duration(self):
        SECONDS_IN_MINUTE = 60
        SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
        SECONDS_IN_DAY = SECONDS_IN_HOUR * 24

        duration = self.get_duration_fields()
        return (
            duration["dur_seconds"]
            + duration["dur_minutes"] * SECONDS_IN_MINUTE
            + duration["dur_hours"] * SECONDS_IN_HOUR
            + duration["dur_days"] * SECONDS_IN_DAY
        )


if __name__ == "__main__":
    app = GuiApp()
    app.run()
