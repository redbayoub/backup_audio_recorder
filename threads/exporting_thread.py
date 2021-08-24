from constants import Constants
from threading import Thread
import time
import os.path
import json
import sounddevice as sd
import soundfile as sf


class ExportingThread(Thread):

    # kwargs = {
    #   "output_directory"
    #  }
    def __init__(
        self,
        finished_callback,
        export_file_path,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs=None,
    ):
        super(ExportingThread, self).__init__(
            group=group,
            target=target,
            name=name,
            daemon=True,
        )
        self.args = args
        self.kwargs = kwargs

        self.export_file_path = export_file_path
        self.exporting_finished_callback = finished_callback

        self.conf_data = None
        self.output_directory = None
        self.rec_pos = 0
        self.rec_out_path = None
        self.__init_conf_data()

    def __init_conf_data(self):
        self.output_directory = self.kwargs["output_directory"]
        if not os.path.isdir(self.output_directory):
            raise Exception("output directory not found")

        self.conf_path = self.output_directory + os.path.sep + Constants.CONF_FILENAME
        if not os.path.isfile(self.conf_path):
            raise Exception("conf file not found")

        self.conf_data = json.load(open(self.conf_path))

        self.rec_pos = self.conf_data["rec_pos"]

        self.rec_out_path = (
            self.output_directory + os.path.sep + Constants.RECORDING_OUTPUT_FILENAME
        )

    def run(self):
        read_pos = self.rec_pos
        with sf.SoundFile(
            self.export_file_path,
            mode="w",
            samplerate=Constants.SAMPLE_RATE,
            channels=Constants.CHANNELS,
            subtype=Constants.SUBTYPE,
        ) as export_f:
            with sf.SoundFile(
                self.rec_out_path,
                samplerate=Constants.SAMPLE_RATE,
                channels=Constants.CHANNELS,
                subtype=Constants.SUBTYPE,
            ) as f:
                f.seek(read_pos)
                initial = True
                data = []
                while initial or len(data):
                    if f.tell() == f.frames and not read_pos == 0:
                        f.seek(0)

                    if f.tell() == read_pos and not initial:
                        break

                    data = f.read(Constants.BLOCKSIZE)
                    export_f.write(data)
                    initial = False
            export_f.close()

        self.exporting_finished_callback()
