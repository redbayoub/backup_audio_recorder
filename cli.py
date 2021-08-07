import argparse
import sys
import os.path
import sounddevice
from threading import Event
import time
from backup_audio_recorder import BackupAudioRecorder

parser = argparse.ArgumentParser(
    description="this script record your audio passively and later then you can get the last n seconds"
)

parser.add_argument(
    "-li",
    "--list-input-devices",
    action="store_true",
    default=False,
    dest="list_input_devices",
    help="list available input devices",
)
parser.add_argument(
    "-lo",
    "--list-output-devices",
    action="store_true",
    default=False,
    dest="list_output_devices",
    help="list available output devices",
)
parser.add_argument(
    "-id",
    "--input-device",
    dest="input_device",
    type=int,
    default=0,
    help="select input device",
)
parser.add_argument(
    "-od",
    "--output-device",
    dest="output_device",
    type=int,
    default=0,
    help="select output device",
)

parser.add_argument(
    "-a",
    "--action",
    dest="action",
    choices=["record", "listen", "export"],
    help="the action to be performed",
)
parser.add_argument(
    "-d",
    "--duration",
    dest="duration",
    type=int,
    help="the duration to be kept recorded in seconds",
)

parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
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

default_input_device=sounddevice.query_devices(kind='input')
default_output_device=sounddevice.query_devices(kind='output')
hostapis_names= [hostapi['name'] for hostapi in sounddevice.query_hostapis()]
audio_devices=sounddevice.query_devices()
input_devices= [device for device in audio_devices if device['max_input_channels'] > 0]
output_devices= [device for device in audio_devices if device['max_output_channels'] > 0]

if args.list_input_devices:
    print(f'0   Default: {default_input_device["name"]}, {hostapis_names[default_input_device["hostapi"]]}')
    for i in range(len(input_devices)):
        print(f'{i+1}   {input_devices[i]["name"]}, {hostapis_names[input_devices[i]["hostapi"]]}')
    exit(0)
    
if args.list_output_devices:
    print(f'0   Default: {default_output_device["name"]}, {hostapis_names[default_output_device["hostapi"]]}')
    for i in range(len(output_devices)):
        print(f'{i+1}   {output_devices[i]["name"]}, {hostapis_names[output_devices[i]["hostapi"]]}')
    exit(0)

# validate args
if not args.action:
    print("error: the following arguments are required: -a/--action")
    exit(1)

if not args.output_dir:
    print("error: the following arguments are required: -o/--output-dir")
    exit(1)

if not args.duration and args.action == "record":
    print("error: the following arguments are required: -d/--duration")
    exit(1)

if args.input_device<0 or args.input_device>len(input_devices):
    print(f"error:  argument -id/--input-device: invalid int value: '{args.input_device}'")
    exit(1)

if args.output_device<0 or args.output_device>len(output_devices):
    print(f"error:  argument -id/--putput-device: invalid int value: '{args.output_device}'")
    exit(1)

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
    input_device= None if args.input_device == 0 else input_devices[args.input_device-1]["name"],
    output_device= None if args.output_device == 0 else output_devices[args.output_device-1]["name"],
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
