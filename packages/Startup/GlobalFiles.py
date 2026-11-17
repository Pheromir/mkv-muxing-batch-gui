import json
import logging
import os
import struct
import subprocess
import sys
from os import listdir
from pathlib import Path

from packages.Widgets.MissingFilesMessage import MissingFilesMessage


def create_app_data_folder():
    """
        Returns a parent directory path
        where persistent application data can be stored.

        # linux: ~/.local/share
        # macOS: ~/Library/Application Support
        # windows: C:/Users/<USER>/AppData/Roaming
        """
    home = Path.home()
    app_data = ""
    if sys.platform == "win32":
        app_data = home / "AppData/Roaming"
    elif sys.platform == "linux":
        app_data = home / ".local/share"
    elif sys.platform == "darwin":
        app_data = home / "Library/Application Support"
    my_app_data_folder = app_data / "MKV Muxing Batch GUI"
    try:
        os.makedirs(my_app_data_folder, exist_ok=True)
    except Exception as e:
        pass
    return my_app_data_folder


def add_double_quotation(string):
    return "\"" + str(string) + "\""


def get_file_name_absolute_path(file_name, folder_path):
    return os.path.join(Path(folder_path), file_name)


def get_files_names_absolute_list(files_names, folder_path):
    result = []
    for i in range(len(files_names)):
        result.append(get_file_name_absolute_path(file_name=files_names[i], folder_path=folder_path))
    return result


def delete_old_media_files():
    only_media_info_files = get_files_names_absolute_list(files_names=listdir(MediaInfoFolderPath),
                                                          folder_path=MediaInfoFolderPath)
    for file_name in only_media_info_files:
        try:
            os.remove(file_name)
        except Exception as e:
            pass


script_path = sys.argv[0]  # get path of the this file
script_folder = os.path.dirname(script_path)
resources_folder = os.path.join(os.path.abspath(script_folder), Path('Resources'))
FontFolderPath = os.path.join(os.path.abspath(resources_folder), Path('Fonts'))
IconFolderPath = os.path.join(os.path.abspath(resources_folder), Path('Icons'))
DLLFolderPath = os.path.join(os.path.abspath(resources_folder), Path('DLL'))
GlobalToolsFolderPath = os.path.join(os.path.abspath(resources_folder), Path('Tools'))
ToolsFolderPath = os.path.join(os.path.abspath(GlobalToolsFolderPath), Path('Windowsx64'))
LanguagesFolderPath = os.path.join(os.path.abspath(resources_folder), Path('Languages'))
LibFolderPath = ""
if sys.platform == "win32":
    if struct.calcsize("P") * 8 == 32:
        ToolsFolderPath = os.path.join(os.path.abspath(GlobalToolsFolderPath), Path('Windows32'))
    else:
        ToolsFolderPath = os.path.join(os.path.abspath(GlobalToolsFolderPath), Path('Windows64'))
elif sys.platform == "linux" or sys.platform == "linux2":
    ToolsFolderPath = os.path.join(os.path.abspath(GlobalToolsFolderPath), Path('Linux'))
    LibFolderPath = os.path.join(os.path.abspath(ToolsFolderPath), Path('lib'))
else:
    ToolsFolderPath = os.path.join(os.path.abspath(GlobalToolsFolderPath), Path('Other Systems'))
AppDataFolderPath = create_app_data_folder()
MKVTOOLNIX_SOURCE_BUNDLED = "Bundled"
MKVTOOLNIX_SOURCE_INSTALLED = "Installed"
PREFERRED_MKVTOOLNIX_SOURCE = MKVTOOLNIX_SOURCE_BUNDLED
MKVMERGE_SOURCE = ""
MKVPROPEDIT_SOURCE = ""
MergeLogsFolderPath = os.path.join(os.path.abspath(AppDataFolderPath), Path('Logs'))
MediaInfoFolderPath = os.path.join(os.path.abspath(AppDataFolderPath), Path('MediaInfo'))
os.makedirs(MergeLogsFolderPath, exist_ok=True)
os.makedirs(MediaInfoFolderPath, exist_ok=True)
delete_old_media_files()


def get_tool_version(tool_path, test_file_path):
    with open(test_file_path, "w+", encoding="UTF-8") as test_file:
        try:
            command = add_double_quotation(tool_path) + " -V"
            subprocess.run(command, shell=True, stdout=test_file, stderr=subprocess.DEVNULL, env=ENVIRONMENT)
        except:
            return ""
    with open(test_file_path, "r+", encoding="UTF-8") as test_file:
        return test_file.readline().rstrip()


def get_mkvmerge_version():
    return get_tool_version(MKVMERGE_PATH, TestMkvmergeFilePath)


def get_mkvpropedit_version():
    return get_tool_version(MKVPROPEDIT_PATH, TestMkvpropeditFilePath)


def get_preferred_mkvtoolnix_source():
    """"Bundled" (default) or "Installed", read directly from the settings file as Options is not loaded yet"""
    try:
        with open(SettingJsonInfoFilePath, "r", encoding="UTF-8") as setting_file:
            source = json.load(setting_file).get("Mkvtoolnix_Source", MKVTOOLNIX_SOURCE_BUNDLED)
    except Exception:
        source = MKVTOOLNIX_SOURCE_BUNDLED
    return source if source in (MKVTOOLNIX_SOURCE_BUNDLED, MKVTOOLNIX_SOURCE_INSTALLED) else MKVTOOLNIX_SOURCE_BUNDLED


def get_installed_tool_candidates(tool_name):
    # the windows installer of MKVToolNix does not add itself to PATH, so check its default folders first
    candidates = []
    if sys.platform == "win32":
        for program_files in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"),
                              os.environ.get("ProgramFiles(x86)")):
            if program_files:
                candidate = os.path.join(program_files, "MKVToolNix", tool_name + ".exe")
                if os.path.isfile(candidate) and candidate not in candidates:
                    candidates.append(candidate)
    candidates.append(tool_name)  # system PATH
    return candidates


def find_tool(tool_name, bundled_path, test_file_path):
    """returns (path, version, source) of the first working tool, the preferred source is tried first"""
    bundled = [(bundled_path, MKVTOOLNIX_SOURCE_BUNDLED)]
    installed = [(path, MKVTOOLNIX_SOURCE_INSTALLED) for path in get_installed_tool_candidates(tool_name)]
    if PREFERRED_MKVTOOLNIX_SOURCE == MKVTOOLNIX_SOURCE_INSTALLED:
        candidates = installed + bundled
    else:
        candidates = bundled + installed
    for path, source in candidates:
        version = get_tool_version(path, test_file_path)
        if tool_name in version:
            if source != PREFERRED_MKVTOOLNIX_SOURCE:
                logging.warning(f"Could not use {PREFERRED_MKVTOOLNIX_SOURCE.lower()} {tool_name}, using {path}")
            return path, version, source
    return bundled_path, "", ""


def update_enviro_if_not_windows():
    if "LD_LIBRARY_PATH" not in ENVIRONMENT.keys():
        ENVIRONMENT["LD_LIBRARY_PATH"] = ""
    if sys.platform != "win32":
        ENVIRONMENT["LD_LIBRARY_PATH"] = f"{Path(LibFolderPath).absolute()}:{ENVIRONMENT['LD_LIBRARY_PATH']}"


try:
    MyFontPath = os.path.join(os.path.abspath(FontFolderPath), 'OpenSans.ttf')
    WarningCheckBigIconPath = os.path.join(os.path.abspath(IconFolderPath), 'WarningCheckBig.png')
    WarningCheckIconPath = os.path.join(os.path.abspath(IconFolderPath), 'WarningCheck.png')
    TrueCheckIconPath = os.path.join(os.path.abspath(IconFolderPath), 'TrueCheck.png')
    GreenTikMarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'GreenTikMark.png')
    RedCrossMarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'RedCrossMark.png')
    ChapterIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Chapter.svg')
    SubtitleLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Subtitle_Light.svg')
    AudioLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Audio_Light.svg')
    SubtitleDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Subtitle_Dark.svg')
    AudioDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Audio_Dark.svg')
    StartMultiplexingIconPath = os.path.join(os.path.abspath(IconFolderPath), 'StartMultiplexing.png')
    PauseMultiplexingIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Pause.png')
    AddToQueueIconPath = os.path.join(os.path.abspath(IconFolderPath), 'AddToQueue.svg')
    InfoSettingIconPath = os.path.join(os.path.abspath(IconFolderPath), 'InfoSetting.svg')
    InfoIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Info.svg')
    AboutIconPath = os.path.join(os.path.abspath(IconFolderPath), 'About.svg')
    NoMarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'NoMark.svg')
    RedDashIconPath = os.path.join(os.path.abspath(IconFolderPath), 'RedDash.svg')
    PlusIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Plus.svg')
    TrashLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Trash_Light.svg')
    TrashDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Trash_Dark.svg')
    RenameIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Rename.png')
    SwitchIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Switch.svg')
    QuestionIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Question.svg')
    InfoBigIconPath = os.path.join(os.path.abspath(IconFolderPath), 'InfoBig.png')
    OkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Ok.png')
    PresetLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Preset_Light.png')
    PresetDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Preset_Dark.png')
    SelectedItemIconPath = os.path.join(os.path.abspath(IconFolderPath), 'SelectedItemIcon.png')
    UnSelectedItemIconPath = os.path.join(os.path.abspath(IconFolderPath), 'UnSelectedItemIcon.png')
    EmptyIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Empty.png')
    ErrorIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Error.png')
    LeftArrowIconPath = os.path.join(os.path.abspath(IconFolderPath), 'LeftArrow.png')
    RightArrowIconPath = os.path.join(os.path.abspath(IconFolderPath), 'RightArrow.png')
    ErrorBigIconPath = os.path.join(os.path.abspath(IconFolderPath), 'ErrorBig.png')
    ClearIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Clear.svg')
    RefreshIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Refresh.png')
    TopLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Top_Light.svg')
    DownLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Down_Light.svg')
    UpLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Up_Light.svg')
    BottomLightIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Bottom_Light.svg')
    TopDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Top_Dark.svg')
    DownDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Down_Dark.svg')
    UpDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Up_Dark.svg')
    BottomDarkIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Bottom_Dark.svg')
    FolderIconPath = os.path.join(os.path.abspath(IconFolderPath), 'SelectFolder.svg')
    SpinnerIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Spinner.gif')
    GoodJobIconPath = os.path.join(os.path.abspath(IconFolderPath), 'GoodJob.png')
    SettingIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Setting.svg')
    ThemeIconPath = os.path.join(os.path.abspath(IconFolderPath), 'Day_And_Night.png')
    AppIconPath = os.path.join(os.path.abspath(IconFolderPath), 'App.ico')
    LanguagesFilePath = os.path.join(os.path.abspath(LanguagesFolderPath), "iso639_language_list.json")
    AppLogFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "app_log.txt")
    MuxingLogFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "muxing_log_file.txt")
    TestMkvmergeFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "test_mkvmerge.txt")
    TestMkvpropeditFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "test_mkvpropedit.txt")
    mkvpropeditJsonJobFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "mkvpropeditJob.json")
    mkvmergeJsonJobFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "MkvmergeJob.json")
    mkvmergeJsonInfoFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "MkvmergeInfo.json")
    SettingJsonInfoFilePath = os.path.join(os.path.abspath(AppDataFolderPath), "setting.json")
    TaskBarLibFilePath = os.path.join(os.path.abspath(DLLFolderPath), "TaskbarLib.tlb")
    MKVPROPEDIT_PATH = os.path.join(os.path.abspath(ToolsFolderPath), "mkvpropedit")
    MKVMERGE_PATH = os.path.join(os.path.abspath(ToolsFolderPath), "mkvmerge")
    ENVIRONMENT = os.environ.copy()
    update_enviro_if_not_windows()
    PREFERRED_MKVTOOLNIX_SOURCE = get_preferred_mkvtoolnix_source()
    MKVMERGE_PATH, MKVMERGE_VERSION, MKVMERGE_SOURCE = find_tool("mkvmerge", MKVMERGE_PATH, TestMkvmergeFilePath)
    if MKVMERGE_VERSION == "":
        MKVMERGE_VERSION = "mkvmerge: not found!"
        raise Exception("mkvmerge file! ")
    logging.info(f"mkvmerge OK ({MKVMERGE_SOURCE}): {MKVMERGE_PATH}")
    MKVPROPEDIT_PATH, MKVPROPEDIT_VERSION, MKVPROPEDIT_SOURCE = find_tool("mkvpropedit", MKVPROPEDIT_PATH,
                                                                          TestMkvpropeditFilePath)
    if MKVPROPEDIT_VERSION == "":
        MKVPROPEDIT_VERSION = "mkvpropedit: not found!"
        raise Exception("mkvpropedit file! ")
    logging.info(f"mkvpropedit OK ({MKVPROPEDIT_SOURCE}): {MKVPROPEDIT_PATH}")
except Exception as e:
    logging.error(e)
    missing_files_message = MissingFilesMessage(error_message=str(e))
    missing_files_message.execute()
