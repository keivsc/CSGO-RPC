from http import server
import requests, time, pypresence,json
from .webserver.payload_parser import Loader
import os

class invalidTokenError(Exception):
    pass

class RPC:
    def __init__(self, client, address, config):
        self.address = address
        self.config = config
        self.startTime = 0
        self.menuTime = 0
        self.client = client
        self.loader = Loader()

    def get_data(self):
        res = requests.get(f'http://{self.address[0]}:{self.address[1]}/data', params={'auth':self.config["GSIServer"]['auth_token']})
        if res.status_code == 200:
            return json.loads(res.content)
        else:
            raise invalidTokenError("Invalid token provided in the config!")

    def run(self, steam):
        while True:
            if not steam.are_processes_running():
                os._exit(1)
            try:
                rData = {}
                data = self.get_data()
                rData['large_image'] = "game_icon"
                rData['large_text'] = "Counter-Strike: Global Offensive"
                if data['activity'] == 'menu':
                    self.startTime = 0
                    if self.menuTime == 0:
                        self.menuTime = time.time()
                    rData['details'] = "Main Menu"
                    rData['start'] = self.menuTime

                elif data['activity'] == 'playing':
                    self.menuTime = 0
                    if self.startTime == 0:
                        self.startTime = time.time()
                    rData['start'] = self.startTime
                    data = data['data']
                    rData['large_image'] = data['map']['asset']
                    rData['large_text'] = data['map']['name'] + " - " + data['map']['mode']
                    rData['small_image'] = data['player']['team']['asset']
                    rData['small_text'] = f"{data['player']['team']['name']} | ${data['player']['state']['money']}"
                    if data['phase'] != "Freeze Time":
                        rData['small_text'] += f" | KAD: {data['player']['match_stats']['kills']}/{data['player']['match_stats']['assists']}/{data['player']['match_stats']['deaths']}"
                        if self.config['presence']['show_weapon']:
                            if len(list(data['player']['weapons'].keys())) != 0:
                                try:
                                    for x in range(3):
                                        weapon = data['player']['weapons'][f'weapon_{x}']
                                        if weapon['state'] == "active":
                                            currentWeapon = "Current Weapon: "+self.loader.data['weapons'][weapon['name'].replace('weapon_', '')]['name']
                                            break
                                except:
                                    currentWeapon = "Dead"
                            else:
                                currentWeapon = "Dead"
                        rData['state'] = currentWeapon
                    if data['map']['mode'] == "Deathmatch":
                        rData['details'] = f"{data['map']['mode']} | KAD: {data['player']['match_stats']['kills']}/{data['player']['match_stats']['assists']}/{data['player']['match_stats']['deaths']}"
                        rData['small_image'] = "deathmatch"
                        rData['small_text'] = f"K/D: {round(data['player']['match_stats']['kills']/data['player']['match_stats']['deaths'], 1)} | KAD: {data['player']['match_stats']['kills']}/{data['player']['match_stats']['assists']}/{data['player']['match_stats']['deaths']} "
                    else:
                        rData['details'] = f"{data['map']['mode']} | {data['phase']} | {data['team_scores']['ally']}:{data['team_scores']['enemy']}"
            except:
                rData['large_image'] = "game_icon"
                rData['large_text'] = "Counter-Strike: Global Offensive"
                rData['details'] = "Main Menu"
                rData['start'] = self.menuTime
            if rData['start'] <1:
                rData['start'] = None
            self.client.update(**rData)
            time.sleep(self.config['presence']['refresh_rate'])
            

