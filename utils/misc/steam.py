import os, psutil, time, winreg
from colorama import Fore

def are_processes_running(required_processes=["csgo.exe"]):
    processes = []
    for proc in psutil.process_iter():
        processes.append(proc.name())
    
    return set(required_processes).issubset(processes)

def startCS(appdata):
    path = os.path.join(appdata, "csgo.url")
    if not "csgo.url" in os.listdir(appdata):
        shortcut = open(path, 'w')
        shortcut.write('[{000214A0-0000-0000-C000-000000000046}]\n')
        shortcut.write(f"""Prop3=19,0
[InternetShortcut]
IDList=
IconIndex=0
URL=steam://rungameid/730
IconFile={appdata}/favicon.ico
HotKey=0""")
        shortcut.close()
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
    except:
        hkey = None
    try:
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")
    except:
        steam_path = None
    if steam_path != None:
        os.startfile(steam_path[0]+r'\steam.exe')
    os.startfile(path)

def run_game(appdata, config):
    launch_timeout = config["startup"]["launch_timeout"]
    launch_timer = 0
    os.system('cls')
    if not are_processes_running():
        startCS(appdata)
    while not are_processes_running():
        print(Fore.RED+f"[...] Waiting for Counter Strike: Global Offensive ({launch_timer}) - Timeout ({launch_timeout})", end="\r")
        time.sleep(1)
        launch_timer+=1
        if launch_timer >= launch_timeout:
            os._exit(1)
    os.system('cls')
    print(f"{Fore.GREEN}[√] CS:GO detected and running!")

