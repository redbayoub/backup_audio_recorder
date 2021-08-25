import soundfile as sf
import os.path
from constants import Constants
import numpy as np


def check_frames_is_rec_pos(frames):
    def check_frame_is_rec_pos(frame):
        return np.array_equal(Constants.REC_POS_SEP[0], frame)

    return check_frame_is_rec_pos(frames[0]) and check_frame_is_rec_pos(frames[-1])


def get_rec_pos(rec_out_path):
    if not os.path.isfile(rec_out_path):
        return 0

    rec_pos = 0
    with sf.SoundFile(
        rec_out_path,
        samplerate=Constants.SAMPLE_RATE,
        channels=Constants.CHANNELS,
        subtype=Constants.SUBTYPE,
    ) as f:
        max_frames = f.frames
        while not f.tell() == max_frames and not check_frames_is_rec_pos(
            f.read(Constants.BLOCKSIZE)
        ):
            rec_pos += Constants.BLOCKSIZE
        f.close()
    return rec_pos
