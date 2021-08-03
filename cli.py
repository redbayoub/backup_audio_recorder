import argparse
import sys
import os.path
from threading import Event
import time
from backup_audio_recorder import BackupAudioRecorder

parser = argparse.ArgumentParser(
    description="this script record your audio passively and later then you can get the last n seconds"
)

parser.add_argument(
    "-a",
    "--action",
    dest="action",
    required=True,
    choices=["record", "listen", "export"],
    help="the action to be performed",
)
parser.add_argument(
    "-d",
    "--duration",
    dest="duration",
    required="record" in sys.argv,
    type=int,
    help="the duration to be kept recorded in seconds",
)

parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    required=True,
    type=str,
    help="the path to the directory where recording are kept",
)

parser.add_argument(
    "-ef",
    "--export-file-path",
    dest="export_file_path",
    required="export" in sys.argv,
    type=str,
    help="the path to the file  where the recording will be exported",
)

args = parser.parse_args()

export_file = None
# validate args
if args.action == "export":
    export_file = args.export_file_path
    if not export_file.endswith(".wav"):
        export_file + ".wav"
    if os.path.isfile(export_file):
        print(
            "ERROR: Export file already exists, Plz use non existing file or remove the existing file"
        )
        exit(1)


def listening_finished_callback():
    print("listening finished")
    recorder.stop_listening()
    stop_action_event.set()


def exporting_finished_callback():
    print("exporting finished")
    recorder.stop_exporting()
    stop_action_event.set()


stop_action_event = Event()
stop_action_event.clear()

recorder = BackupAudioRecorder(
    output_directory=args.output_dir,
    listening_finished_callback=listening_finished_callback,
    exporting_finished_callback=exporting_finished_callback,
)

try:
    if args.action == "record":
        recorder.start_recording(args.duration)
        print("recording started")

    elif args.action == "listen":
        recorder.start_listening()
        print("listening started")

    else:  # export
        recorder.start_exporting(export_file)
        print("exporting started")

    print("Press Ctrl+C to stop the current action")
    while not stop_action_event.is_set():
        time.sleep(1)

except KeyboardInterrupt:
    stop_action_event.set()
    print("action stooped by user")
finally:
    if args.action == "record" and recorder.is_recording:
        recorder.stop_recording()
        print("recording stopped")

    elif args.action == "listen" and recorder.is_listening:
        recorder.stop_listening()
        print("listening stopped")

    elif recorder.is_exporting:  # export
        recorder.stop_exporting()
        print("exporting stopped")
