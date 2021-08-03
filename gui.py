from constants import Constants
import validators
from backup_audio_recorder import BackupAudioRecorder
import dialogs
import os
import json
import tkinter as tk
import pygubu
from pygubu.builder import tkstdwidgets

PRIMARY_COLOR = "#1492e6"


PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "gui.ui")


USER_HOME_DIR_PATH = os.path.expanduser("~")
PROJECT_LOCAL_DIR_PATH = os.path.join(USER_HOME_DIR_PATH, ".passive_recorder")
PROJECT_CONF_PATH = os.path.join(PROJECT_LOCAL_DIR_PATH, "conf.json")
PROJECT_DEFAULT_REC_OUTPUT_PATH = os.path.join(PROJECT_LOCAL_DIR_PATH, "recordings")


class GuiApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object("mainwindow", master)

        builder.connect_callbacks(self)

        os.makedirs(PROJECT_DEFAULT_REC_OUTPUT_PATH, exist_ok=True)

        self.conf_data = {}
        if not os.path.isfile(PROJECT_CONF_PATH):
            self.conf_data = {
                "output_directory": PROJECT_DEFAULT_REC_OUTPUT_PATH,
                "dur_days": 0,
                "dur_hours": 0,
                "dur_minutes": 0,
                "dur_seconds": 0,
            }
            json.dump(self.conf_data, open(PROJECT_CONF_PATH, "w"))
        else:
            self.conf_data = json.load(open(PROJECT_CONF_PATH))

        self.__set_entry("location_entry", self.conf_data["output_directory"])
        self.__set_entry("days_dur_entry", self.conf_data["dur_days"])
        self.__set_entry("hours_dur_entry", self.conf_data["dur_hours"])
        self.__set_entry("minutes_dur_entry", self.conf_data["dur_minutes"])
        self.__set_entry("seconds_dur_entry", self.conf_data["dur_seconds"])

        self.recorder = BackupAudioRecorder(
            output_directory=self.conf_data["output_directory"],
            listening_finished_callback=self.listen,
            exporting_finished_callback=self.export,
        )

    def load_conf_data_from_output_dir(self, output_dir):
        rec_conf_path = os.path.join(output_dir, Constants.CONF_FILENAME)
        if os.path.isfile(rec_conf_path):
            rec_conf_data = json.load(open(rec_conf_path))
            self.__set_entry("days_dur_entry", 0)
            self.__set_entry("hours_dur_entry", 0)
            self.__set_entry("minutes_dur_entry", 0)
            # we substract one because it is added in recordding thread directly
            self.__set_entry("seconds_dur_entry", rec_conf_data["duration"]-1)



    def browse(self):
        output_dir_path = dialogs.ask_folder(
            initialdir=self.conf_data["output_directory"]
        )
        if output_dir_path:
            self.__set_entry("location_entry", output_dir_path)
            self.recorder.set_output_directory(output_dir_path)
            self.load_conf_data_from_output_dir(output_dir_path)
            self.__save_conf()

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
            self.__save_conf()
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

    def run(self):
        self.mainwindow.mainloop()

    def __save_conf(self):
        location = self.builder.get_variable("location").get()
        dur_seconds = self.builder.get_variable("dur_seconds").get()
        dur_minutes = self.builder.get_variable("dur_minutes").get()
        dur_hours = self.builder.get_variable("dur_hours").get()
        dur_days = self.builder.get_variable("dur_days").get()
        self.conf_data = {
            "output_directory": location,
            "dur_days": dur_days,
            "dur_hours": dur_hours,
            "dur_minutes": dur_minutes,
            "dur_seconds": dur_seconds,
        }
        json.dump(self.conf_data, open(PROJECT_CONF_PATH, "w"))

    def __set_entry(self, entry_id, value):
        entry = self.builder.get_object(entry_id)
        initial_entry_state = entry["state"]
        if not initial_entry_state == "normal":
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        if not initial_entry_state == "normal":
            entry.configure(state=initial_entry_state)

    def __get_duration(self):
        SECONDS_IN_MINUTE = 60
        SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
        SECONDS_IN_DAY = SECONDS_IN_HOUR * 24

        dur_seconds = self.builder.get_variable("dur_seconds").get()
        dur_minutes = self.builder.get_variable("dur_minutes").get()
        dur_hours = self.builder.get_variable("dur_hours").get()
        dur_days = self.builder.get_variable("dur_days").get()

        return (
            dur_seconds
            + dur_minutes * SECONDS_IN_MINUTE
            + dur_hours * SECONDS_IN_HOUR
            + dur_days * SECONDS_IN_DAY
        )


if __name__ == "__main__":
    app = GuiApp()
    app.run()
