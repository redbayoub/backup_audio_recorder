# Backup Audio Recorder

## Building for windows

*Command generated using auto-py-to-exe package*

    pyinstaller --noconfirm --onefile --windowed --icon "D:/Scripts/backup_audio_recorder/icon.ico" --name "Backup Audio Recorder" --add-data "D:/Scripts/backup_audio_recorder/constants.py;." --add-data "D:/Scripts/backup_audio_recorder/dialogs.py;." --add-data "D:/Scripts/backup_audio_recorder/gui.ui;." --add-data "D:/Scripts/backup_audio_recorder/backup_audio_recorder.py;." --add-data "D:/Scripts/backup_audio_recorder/validators.py;." --add-data "D:/Scripts/backup_audio_recorder/threads;threads/" --add-data "D:/Scripts/backup_audio_recorder/icon.ico;." --add-data "D:/Scripts/backup_audio_recorder/utils.py;."  "D:/Scripts/backup_audio_recorder/gui.py"
