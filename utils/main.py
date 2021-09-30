from .misc import config, steam
from .webserver import webserver
import pypresence
from .rpc import RPC
import ctypes
import threading
from .systray import systray
import requests
import os
from .misc.logger import Logging

log = Logging(config.Config.create_appdata())

def instance_check(address, auth_token):
    try:
        res = requests.get(f"http://{address[0]}:{address[1]}/data", params={"auth":auth_token})
        if res.status_code == 200:
            log.createLog('LOG', f"CSGO-RPC instance already opened, go to http://{address[0]}:{address[1]}/shutdown to close it")
            os._exit(1)
    except:
        pass

def main():
    log.createLog('LOG', 'CSGO-RPC Started')
    Config = config.Config(log)
    conf = Config.fetchConfig()
    appdata = Config.get_appdata_folder()
    rpc_client = pypresence.Presence(874499526910701598)
    address = ("127.0.0.1", conf["GSIServer"]['port'])
    instance_check(address, conf["GSIServer"]['auth_token'])
    rpc_client.connect()
    data = {
        "details":"Loading...",
        "large_image":"game_icon",
        "large_text":"Counter Strike: Global Offensive"
    }
    if conf['startup']['show_github_link'] == True:
        data['small_image'] = "github"
        data['small_text'] = "keivsc/CSGO-RPC"
        data['buttons'] = []
        data['buttons'].append({"label":"View on GitHub", "url":"https://github.com/keivsc/CSGO-RPC"})
    rpc_client.update(**data)
    systrayThread = threading.Thread(target=systray(Config).run)
    systrayThread.start()
    steam.run_game(appdata, conf)
    rpc = RPC(rpc_client, address, conf)
    webserver.run(address, conf["GSIServer"]['auth_token'])
    print("CSGO Presence Started | Window Hidden")
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    hWnd = kernel32.GetConsoleWindow()
    user32.ShowWindow(hWnd, 0)
    rpc.run(steam)
