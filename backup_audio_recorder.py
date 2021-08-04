import os.path
from threading import Event
from threads.exporting_thread import ExportingThread
from threads.listening_thread import ListeningThread
from threads.recording_thread import RecordingThread


class BackupAudioRecorder:

    output_directory = None
    listening_finished_callback = None
    exporting_finished_callback = None
    

    recording_thread = None
    listening_thread = None
    exporting_thread = None

    stop_recording_event = None
    stop_listening_event = None

    is_recording = False
    is_listening = False
    is_exporting = False

    def __init__(
        self, output_directory, listening_finished_callback, exporting_finished_callback
    ):

        self.listening_finished_callback = listening_finished_callback
        self.exporting_finished_callback = exporting_finished_callback
        if not os.path.isdir(output_directory):
            raise Exception("output directory not found")
        self.output_directory = output_directory

    def set_output_directory(self, value):
        if not os.path.isdir(value):
            raise Exception("output directory not found")
        self.output_directory = value

    def start_recording(self, duration):
        if self.is_recording or self.is_listening or self.is_exporting:
            return False
        self.stop_recording_event = Event()
        self.recording_thread = RecordingThread(
            stop_event=self.stop_recording_event,
            kwargs={"duration": duration, "output_directory": self.output_directory},
        )
        self.is_recording = True
        self.stop_recording_event.clear()
        self.recording_thread.start()
        return True

    def stop_recording(self):
        if not self.is_recording:
            return False
        self.is_recording = False
        self.stop_recording_event.set()
        self.recording_thread.join()

        self.recording_thread = None
        return True

    def start_listening(self):
        if self.is_recording or self.is_listening or self.is_exporting:
            return False

        self.stop_listening_event = Event()
        self.listening_thread = ListeningThread(
            stop_event=self.stop_listening_event,
            finished_callback=self.listening_finished_callback,
            kwargs={"output_directory": self.output_directory},
        )
        self.stop_listening_event.clear()
        self.is_listening = True
        self.listening_thread.start()
        return True

    def stop_listening(self):
        if not self.is_listening:
            return False
        self.is_listening = False
        self.stop_listening_event.set()
        self.listening_thread = None
        return True

    def start_exporting(self, export_file_path):
        if self.is_recording or self.is_listening or self.is_exporting:
            return False

        self.exporting_thread = ExportingThread(
            export_file_path=export_file_path,
            finished_callback=self.exporting_finished_callback,
            kwargs={"output_directory": self.output_directory},
        )
        self.is_exporting = True
        self.exporting_thread.start()
        return True

    def stop_exporting(self):
        self.is_exporting = False
        self.exporting_thread = None
        return True
