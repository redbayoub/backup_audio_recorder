import numpy as np


class Constants:
    FILE_POS_PER_SECOND = 43500  # 43500 pos for 1s
    SUBTYPE = "PCM_24"
    SAMPLE_RATE = 44100
    CHANNELS = 2
    BLOCKSIZE = 500  # 500
    BUFFERSIZE = 30
    CONF_FILENAME = "conf.pr"
    RECORDING_OUTPUT_FILENAME = "rec.raw"
    D_TYPE = "float32"
    REC_POS_SEP = np.full((BLOCKSIZE, 2), [-1, 0], dtype=D_TYPE)
