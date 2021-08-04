from constants import Constants
from threading import Thread
import os.path
import json
import sounddevice as sd
import soundfile as sf


class RecordingThread(Thread):

    # kwargs = {
    #   "output_directory","duration"
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
        )
        self.args = args
        self.kwargs = kwargs

        self.stop_event = stop_event
        self.conf_data = None
        # i add one second to duration to mak sure that it shows on other programs exactly
        self.duration = self.kwargs["duration"] + 1
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
            self.conf_data = {
                "rec_pos": 0,
                "duration": self.duration,
            }
            json.dump(self.conf_data, open(self.conf_path, "w"))
        else:
            self.conf_data = json.load(open(self.conf_path))

        self.rec_pos = self.conf_data["rec_pos"]

        # if the duration changed we save the new duration&
        self.conf_data["duration"] = self.duration

        self.rec_out_path = (
            self.output_directory + os.path.sep + Constants.RECORDING_OUTPUT_FILENAME
        )

    def run(self):
        with sf.SoundFile(
            self.rec_out_path,
            mode="r+",
            samplerate=Constants.SAMPLE_RATE,
            channels=Constants.CHANNELS,
            subtype=Constants.SUBTYPE,
        ) as outfile:
            try:
                outfile.seek(self.rec_pos, sf.SEEK_SET)

                def in_callback(indata, frames, time, status):

                    outfile.write(indata)

                    if outfile.tell() >= self.duration * Constants.FILE_POS_PER_SECOND:
                        outfile.seek(0, sf.SEEK_SET)
                    self.rec_pos = outfile.tell()

                    self.conf_data["rec_pos"] = self.rec_pos
                    json.dump(self.conf_data, open(self.conf_path, "w"))

                with sd.InputStream(
                    channels=Constants.CHANNELS,
                    callback=in_callback,
                    samplerate=Constants.SAMPLE_RATE,
                    blocksize=Constants.BLOCKSIZE,
                ):
                    self.stop_event.wait()
                    # saving_conf_thread.join()

            finally:
                outfile.close()
