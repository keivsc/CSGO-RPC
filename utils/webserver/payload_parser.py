import io
import requests
import vdf

class Loader:
    def __init__(self):
        self.data = {
            "gamemodes":{},
            "maps":{},
            "teams":{
                "t":{"name":"Terrorist", "asset":"t_icon"},
                "ct":{"name":"Counter-Terrorist", "asset":"ct_icon"},
            },
            "weapons":{
                "c4":{"name":"C4 Explosive"},		
                "knife":{"name":"Knife"},
                "knife_t":{"name":"Knife"},
                "taser":{"name":"Zeus"},		
                "shield":{"name":"Shield"},		
                "bumpmine":{"name":"Bump Mines"},		
                "breachcharge":{"name":"C4 Explosive by remote"},		
                "decoy":{"name":"Decoy Grenade"},		
                "flashbang":{"name":"Flashbang"},		
                "healthshot":{"name":"Medi-Shot"},		
                "hegrenade":{"name":"High Explosive Grenage"},		
                "incgrenade":{"name":"Incendiary Grenade"},		
                "molotov":{"name":"Molotov"},	
                "smokegrenade":{"name":"Smoke Grenade"},		
                "tagrenade":{"name":"Tactical Awareness Grenade"},		
                "m249":{"name":"M249"},		
                "mag7":{"name":"MAG-7"},		
                "negev":{"name":"Negev"},		
                "nova":{"name":"Nova"},		
                "sawedoff":{"name":"Sawed-off"},		
                "xm1014":{"name":"XM1014"},	
                "cz75a":{"name":"CZ75-Auto"},		
                "deagle":{"name":"Desert Eagle"},		
                "elite":{"name":"Dual Berettas"},		
                "fiveseven":{"name":"Five-SeveN"},		
                "glock":{"name":"Glock-18"},		
                "hkp2000":{"name":"P2000"},	
                "p250":{"name":"P250"},	
                "revolver":{"name":"R8 Revolver"},		
                "tec9":{"name":"Tec-9"},		
                "usp_silencer":{"name":"USP-S"},		
                "ak47":{"name":"AK-47"},		
                "aug":{"name":"AUG"},		
                "awp":{"name":"AWP"},		
                "famas":{"name":"FAMAS"},		
                "g3sg1":{"name":"G3SG1"},	
                "galilar":{"name":"Galil AR"},	
                "m4a1":{"name":"M4A4"},	
                "m4a1_silencer":{"name":"M4A1-S"},		
                "scar20":{"name":"SCAR-20"},	
                "sg556":{"name":"SG 553"},		
                "ssg08":{"name":"ssg 08"},		
                "bizon":{"name":"PP-Bizon"},		
                "mac10":{"name":"MAC-10"},	
                "mp5sd":{"name":"MP5-SD"},		
                "mp7":{"name":"MP7"},		
                "mp9":{"name":"MP9"},		
                "p90":{"name":"P90"},	
                "ump45":{"name":"UMP-45"}
            }
        }

    def activate(self):
        res = requests.get("https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/resource/csgo_english.txt")
        vdfItems = vdf.parse(io.StringIO(res.content.decode("utf8")))
        tokens = vdfItems['lang']['Tokens']
        for x in list(tokens.keys()):
            if x.startswith('SFUI_Map_'):  
                self.data["maps"][x.replace('SFUI_Map_', '').lower()] = tokens[x]
            
            elif x.startswith('SFUI_GameMode_'):
                self.data["gamemodes"][x.replace('SFUI_GameMode_', '').lower()] = tokens[x]

            else:
                continue

phases = {
	"freezetime": "Freeze Time",
	"live": "In Game",
	"over": "Round Over",
	"warmup": "Warmup",
    "gameover":"Game Over"
}

loader = Loader()
loader.activate()
pastActivity = None

scores = {
    't':'ct',
    'ct':'t'
}

class Parser:
    def __init__(self):
        self.user = None
    
    def parsePayload(self, payload):
        global pastActivity
        if self.user == None:
            self.user = payload['player']['steamid']
        
        if payload['player']['steamid'] != self.user:
            return pastActivity
        data = {
            "auth":payload['auth']['token'],
            "activity":payload['player']['activity'].lower(),
            "data":{}
        }
        if data['activity'] == "playing":
            mode = payload['map']['mode']
            gmap = payload['map']['name']
            asset = payload['map']['name']
            if mode not in list(loader.data['gamemodes'].keys()):
                print(mode)
                mode = "custom"
            if gmap not in list(loader.data['maps'].keys()):
                gmap = gmap.split('/')[-1]
                asset = "workshop"
            else:
                gmap=loader.data['maps'][gmap]
            data['data']['map'] = {"name":gmap, "asset":asset, "mode":loader.data['gamemodes'][mode]}
            data['data']['team_scores'] = {}
            try:
                data['data']['team_scores']['ally'] = payload['map'][f'team_{payload["player"]["team"].lower()}']['score']
                data['data']['team_scores']['enemy'] = payload['map'][f'team_{scores[payload["player"]["team"].lower()]}']['score']
            except:
                data['data']['team_scores']['ally'] = 0
                data['data']['team_scores']['enemy'] = 0
            try:
                data['data']['phase'] = phases[payload['round']['phase']]
            except:
                data['data']['phase'] = "Warmup"
            data['data']['player'] = payload['player']
            data['data']['player']['team'] = loader.data['teams'][payload['player']['team'].lower()]
            
        elif data['activity'] == 'menu':
            data['data'] = None

        else:
            data = pastActivity

        pastActivity = data

        return data



