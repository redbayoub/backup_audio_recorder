from constants import Constants
from threading import Thread
import os.path
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

        self.output_directory = None
        self.rec_out_path = None
        self.__init_conf_data()

    def __init_conf_data(self):
        self.output_directory = self.kwargs["output_directory"]
        if not os.path.isdir(self.output_directory):
            raise Exception("output directory not found")

        self.rec_out_path = (
            self.output_directory + os.path.sep + Constants.RECORDING_OUTPUT_FILENAME
        )

    def run(self):
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
                data = f.read(Constants.BLOCKSIZE)
                while len(data):
                    export_f.write(data)
                    data = f.read(Constants.BLOCKSIZE)
            export_f.close()

        self.exporting_finished_callback()
