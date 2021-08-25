import json
import os

USER_HOME_DIR_PATH = os.path.expanduser("~")
PROJECT_LOCAL_DIR_PATH = os.path.join(USER_HOME_DIR_PATH, ".backup_audio_recorder")
PROJECT_CONF_PATH = os.path.join(PROJECT_LOCAL_DIR_PATH, "conf.json")
PROJECT_DEFAULT_REC_OUTPUT_PATH = os.path.join(PROJECT_LOCAL_DIR_PATH, "recordings")


class UiConfController:
    DEFAULT_CONF = {
        "output_directory": PROJECT_DEFAULT_REC_OUTPUT_PATH,
        "dur_days": 0,
        "dur_hours": 0,
        "dur_minutes": 0,
        "dur_seconds": 10,
        "startup_recording": False,
        "startup_minimize": False,
        "input_device": None,
        "output_device": None,
    }

    def __init__(self):

        os.makedirs(PROJECT_DEFAULT_REC_OUTPUT_PATH, exist_ok=True)

        if not os.path.isfile(PROJECT_CONF_PATH):
            self.load_default_conf()
        else:
            try:
                self.load_conf()
            except json.decoder.JSONDecodeError:
                self.load_default_conf()

    def load_default_conf(self):
        print('loading default conf')
        self.conf_data = self.DEFAULT_CONF
        self.save_conf()

    def save_conf(self):
        json.dump(self.conf_data, open(PROJECT_CONF_PATH, "w"))

    def load_conf(self):
        self.conf_data = json.load(open(PROJECT_CONF_PATH))

    def get_conf(self, key):
        try:
            return self.conf_data[key]
        except KeyError:
            return self.DEFAULT_CONF[key]   
            
    def get_default_conf(self, key):
        return self.DEFAULT_CONF[key]

    def set_conf(self, key, value, auto_save=True):
        self.conf_data[key] = value
        if auto_save:
            self.save_conf()
