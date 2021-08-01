import platform
import sys
try:
    from tkinter import Tk
except ImportError:
    try:
        from Tkinter import Tk
    except ImportError:
        # If no versions of tkinter exist (most likely linux) provide a message
        if sys.version_info.major < 3:
            print("Error: Tkinter not found")
            print('For linux, you can install Tkinter by executing: "sudo apt-get install python-tk"')
            sys.exit(1)
        else:
            print("Error: tkinter not found")
            print('For linux, you can install tkinter by executing: "sudo apt-get install python3-tk"')
            sys.exit(1)
try:
    from tkinter.filedialog import askdirectory, asksaveasfilename
except ImportError:
    from tkFileDialog import askdirectory, asksaveasfilename



def ask_folder(initialdir):
    """ Ask the user to select a folder """
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder = askdirectory(parent=root,initialdir=initialdir)
    root.update()
    root.destroy()
    return folder if bool(folder) else None


def ask_file_save_location(file_type):
    """ Ask the user where to save a file """
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    if (file_type is None) or (platform.system() == "Darwin"):
        file_path = asksaveasfilename(parent=root)
    else:
        if file_type == 'wav':
            file_types = [('Wav Files', '*.wav')]
        else:
            file_types = [('All files', '*')]
        file_path = asksaveasfilename(parent=root, filetypes=file_types)
    root.update()
    root.destroy()
    if bool(file_path):
        if file_type == 'wav':
            return file_path if file_path.endswith('.wav') else file_path + '.wav'
        else:
            return file_path
    else:
        return None