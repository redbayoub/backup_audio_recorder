from constants import Constants
from threading import Thread, Event
from queue import Queue, Empty
import time
import os.path
import json
import sounddevice as sd
import soundfile as sf


class ListeningThread(Thread):
    # kwargs = {
    #   "output_directory","output_device"
    #  }
    def __init__(
        self,
        stop_event,
        finished_callback,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs=None,
    ):
        super(ListeningThread, self).__init__(
            group=group,
            target=target,
            name=name,
            daemon=True,
        )
        self.args = args
        self.kwargs = kwargs

        self.stop_event = stop_event
        self.listening_finished_callback = finished_callback
        self.conf_data = None

        self.output_directory = None
        self.output_device = self.kwargs["output_device"]
        self.rec_pos = 0
        self.duration = 0
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
        self.duration = self.conf_data["duration"]

        self.rec_out_path = (
            self.output_directory + os.path.sep + Constants.RECORDING_OUTPUT_FILENAME
        )

    def run(self):
        q = Queue(maxsize=Constants.BUFFERSIZE)
        event = Event()

        def callback(outdata, frames, time, status):
            assert frames == Constants.BLOCKSIZE
            if status.output_underflow:
                # print("Output underflow: increase blocksize?")
                raise sd.CallbackAbort
            assert not status
            try:
                data = q.get_nowait()
            except Empty as e:
                # print("Buffer is empty: increase buffersize?")
                raise sd.CallbackAbort from e
            if len(data) < len(outdata):
                # print("raise sd.CallbackStop")
                outdata[: len(data)] = data
                outdata[len(data) :].fill(0)
                raise sd.CallbackStop
            else:
                outdata[:] = data

        with sf.SoundFile(
            self.rec_out_path,
            samplerate=Constants.SAMPLE_RATE,
            channels=Constants.CHANNELS,
            subtype=Constants.SUBTYPE,
        ) as f:

            file_is_looping = f.frames == self.duration * Constants.FILE_POS_PER_SECOND

            if file_is_looping:
                # file is looping
                read_pos = self.rec_pos
                f.seek(read_pos)
            else:  # file is not looping
                read_pos = 0

            data = f.read(Constants.BLOCKSIZE)
            q.put_nowait(data)
            for i in range(1, Constants.BUFFERSIZE):
                if file_is_looping and f.tell() == f.frames:
                    f.seek(0)

                if (file_is_looping and f.tell() == self.rec_pos) or (
                    not file_is_looping and f.tell() == f.frames
                ):
                    data = []
                    break

                data = f.read(Constants.BLOCKSIZE)
                q.put_nowait(data)  # Pre-fill queue
            stream = sd.OutputStream(
                samplerate=f.samplerate,
                blocksize=Constants.BLOCKSIZE,
                channels=f.channels,
                callback=callback,
                finished_callback=event.set,
                device=self.output_device
            )
            with stream:
                timeout = Constants.BLOCKSIZE * Constants.BUFFERSIZE / f.samplerate
                while len(data) and not event.is_set() and not self.stop_event.is_set():

                    if file_is_looping and f.tell() == f.frames:
                        f.seek(0)

                    if (file_is_looping and f.tell() == self.rec_pos) or (
                        not file_is_looping and f.tell() == f.frames
                    ):
                        data = []
                        break

                    data = f.read(Constants.BLOCKSIZE)

                    q.put(data, timeout=timeout)
                # Wait until playback is finished
                while not event.is_set() and not self.stop_event.is_set():
                    time.sleep(1)

                if event.is_set() and not self.stop_event.is_set():
                    self.listening_finished_callback()
