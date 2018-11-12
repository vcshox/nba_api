import requests
import json
from shutil import copyfile

def update_roster(link, file_path):
	response = requests.get(link).json()
	player_list = response['league']['standard']

	with open(file_path, 'r') as roster_file:
		roster_json = json.load(roster_file)
		for player in player_list:
			person_id = player['personId']
			if person_id not in roster_json:
				roster_json[person_id] = player
			
		roster_file.close()

	copyfile(file_path, file_path + '.bak')

	with open(file_path, 'w') as roster_file:
		roster_file.write(json.dumps(roster_json, indent=2))
		roster_file.close()

	return roster_json

api_base = 'http://data.nba.net/10s/'
link_reference_link = api_base + 'prod/v1/today.json'
response = requests.get(link_reference_link).json()

file_path = {
	'roster': 'nba/roster.json',
	'schedule': 'nba/player_stats.json'
}

# latest_roster = update_roster(api_base + response['links']['leagueRosterPlayers'], file_path['roster'])

response = requests.get(api_base + response['links']['leagueSchedule']).json()
game_list = response['league']['standard']

for game in game_list:
	if 'tags' in game and 'PRESEASON' in game['tags']:
		continue

	print game['gameId']
