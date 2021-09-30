from plyer.facades import notification
import requests
import json
import os
import sys, time
from plyer import notification
from colorama import Fore
import sys
import winreg, traceback
import vdf, io

log = None

class SteamNotFound(Exception):
    pass
class CSNotInstalled(Exception):
    pass
class CFGNotCreated(Exception):
    pass

def fetchTag():
    req = requests.get("https://api.github.com/repos/keivsc/csgo-rpc/releases/latest")
    try:
        tag = req.json()["tag_name"]
    except:
        tag = 0
    return tag

latestVersion = fetchTag()
currentVersion = "v1"
latestConfig = {}
translationFile = {}

def configActivate():
    globals()['latestConfig'] = (requests.get(f"https://raw.githubusercontent.com/keivsc/csgo-rpc/{currentVersion}/configExample.json")).json()

def get_steam_path():
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
    except:
        hkey = None
    try:
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")
    except:
        steam_path = None
    if steam_path == None:
        raise SteamNotFound("Unable to find steam installation path")
    library = steam_path[0]+r"\steamapps\libraryfolders.vdf"
    file = open(library, 'rb')
    f = file.read()
    lib = vdf.parse(io.StringIO(f.decode('utf-8')))
    items = lib['libraryfolders']
    items.pop("contentstatsid")
    for x in list(items.keys()):
        for y in list(items[x]['apps'].keys()):
            if y == "730":
                steam_path = items[x]['path']
                log.createLog('LOG', f"Steam Path: {steam_path}")
                return steam_path
    return steam_path[0]

def create_cfg(steam_path):
    csgo_path = steam_path+r"\steamapps\common\Counter-Strike Global Offensive"
    if os.path.isdir(csgo_path):
        cfg_path = csgo_path+r"\csgo\cfg\gamestate_integration_csgorpc.cfg"
        if os.path.isfile(cfg_path):
            return True, cfg_path
        try:
            with open(cfg_path, 'a+') as f:
                res = requests.get("https://raw.githubusercontent.com/keivsc/CSGO-RPC/v1/gamestate_integration_csgorpc.cfg")
                f.write(str(res.content.decode('utf-8')))
                f.close()
        except:
            return False, cfg_path
        return True, cfg_path
    else:
        log.createLog('ERR', f"CS:GO path does not exist: {csgo_path}")
        raise CSNotInstalled("CS:GO is not installed on this machine!")

class Config:
    def __init__(self, logger) -> None:
        self.checkConfig()
        global log
        log = logger
        print(f"Checking for gamestate integration cfg file...")
        try:
            cfg, cfg_path = create_cfg(get_steam_path())
            
        except Exception as e:
            traceback.print_exc()
            input(e)
        else:
            if cfg == False:
                print(f"Unable to create gamestate_integration.cfg\nManually download gamestate cfg from the github and paste it into {cfg_path}")
                input("Press enter to continue...")
                cfg, cfg_path = create_cfg(get_steam_path())
                if cfg == False:
                    os._exit(1)
        os.system('cls')
        print(f"{cfg_path} Found!")
        log.createLog('LOG', f'GIS cfg file: {cfg_path}')

    @staticmethod
    def create_appdata():
        path = os.path.join(os.getenv('APPDATA'), 'CSGO-RPC')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @staticmethod 
    def get_path(relative_path):
        if hasattr(sys, '_MEIPASS'): 
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def checkVersion(self):
        try:
            newConf = self.fetchConfig()
            newConf['version'] = currentVersion
            self.updateConf(newConf)
            if latestVersion != currentVersion:
                print(f"{Fore.YELLOW}There is a new version of CSGO-RPC ({currentVersion} -> v{latestVersion})\n{Fore.GREEN}Download it at\nhttps://github.com/keivsc/CSGO-RPC/releases/latest")
                return True
        except:
            print(f"{Fore.RED}Unable to check for new versions")
            

    def checkConfig(self):
        configActivate()
        newConf = latestConfig
        newConf['version'] = currentVersion
        conf = self.updateConf(newConf)
        if self.checkVersion() == True:
            notification.notify(
                title='New Version of RPC is available',
                message='Check out keivsc/CSGO-RPC for the new version!',
                app_icon=self.get_path(os.path.join(self.get_appdata_folder(), 'favicon.ico'))
            )
        else:
            print(f"{Fore.GREEN}CS:GO RPC Up To Date")
        time.sleep(3)
        return conf

    def get_appdata_folder(self):
        return self.get_path(os.path.join(os.getenv('APPDATA'), 'CSGO-RPC'))

    def fetchConfig(self):
        try:
            with open(self.get_path(os.path.join(self.get_appdata_folder(), "config.json"))) as f:
                config = json.load(f)
                return config
        except:
            return self.createConf()

    def createConf(self):
        if not os.path.exists(self.get_appdata_folder()):
            os.mkdir(self.get_appdata_folder())
        with open(self.get_path(os.path.join(self.get_appdata_folder(), "config.json")), "w") as f:
            latestConfig["version"] = currentVersion
            json.dump(latestConfig, f, indent=4)
        return self.fetchConfig()

    def updateConf(self, data):
        with open(self.get_path(os.path.join(self.get_appdata_folder(), "config.json")), "w") as f:
            json.dump(data, f, indent=4)
        return self.fetchConfig()
