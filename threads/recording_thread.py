from threads.file_utils import get_rec_pos
from constants import Constants
from threading import Thread
import os.path
import json
import sounddevice as sd
import soundfile as sf
import numpy as np


class RecordingThread(Thread):

    # kwargs = {
    #   "output_directory","duration","input_device"
    #  }
    def __init__(
        self,
        stop_event,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs=None,
    ):
        super(RecordingThread, self).__init__(
            group=group,
            target=target,
            name=name,
            daemon=True,
        )
        self.args = args
        self.kwargs = kwargs

        self.stop_event = stop_event
        self.conf_data = None
        # i add one second to duration to mak sure that it shows on other programs exactly
        self.duration = self.kwargs["duration"] + 1
        self.input_device = self.kwargs["input_device"]
        self.output_directory = None
        self.rec_pos = 0
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
        rec_pos = get_rec_pos(self.rec_out_path)
        with sf.SoundFile(
            self.rec_out_path,
            mode="r+",
            samplerate=Constants.SAMPLE_RATE,
            channels=Constants.CHANNELS,
            subtype=Constants.SUBTYPE,
        ) as outfile:
            try:
                outfile.seek(rec_pos, sf.SEEK_SET)

                def in_callback(indata, frames, time, status):
                    if not outfile.tell() == 0:
                        outfile.seek(-Constants.BLOCKSIZE, sf.SEEK_CUR)

                    outfile.write(np.append(indata, Constants.REC_POS_SEP, axis=0))

                    if outfile.tell() >= self.duration * Constants.FILE_POS_PER_SECOND:
                        outfile.seek(0, sf.SEEK_SET)

                with sd.InputStream(
                    channels=Constants.CHANNELS,
                    callback=in_callback,
                    samplerate=Constants.SAMPLE_RATE,
                    blocksize=Constants.BLOCKSIZE,
                    device=self.input_device,
                    dtype=Constants.D_TYPE,
                ):
                    self.stop_event.wait()

            finally:
                outfile.close()
