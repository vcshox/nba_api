import requests
import json
import datetime
import sys
from shutil import copyfile

date_today = datetime.datetime.today()

def backup_file(file_path):
	backup_path = '%s.%s.bak' % (file_path, date_today.strftime('%Y%m%d'))
	copyfile(file_path, backup_path)

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

	backup_file(file_path)

	with open(file_path, 'w') as roster_file:
		roster_file.write(json.dumps(roster_json, indent=2))
		roster_file.close()

	return roster_json

api_base = 'http://data.nba.net/10s/'
link_reference_link = api_base + 'prod/v1/today.json'
response = requests.get(link_reference_link).json()

file_path = {
	'roster': 'nba/roster.json',
	'player_stats': 'nba/player_stats.json'
}

latest_roster = update_roster(api_base + response['links']['leagueRosterPlayers'], file_path['roster'])

response = requests.get(api_base + response['links']['leagueSchedule']).json()
game_list = response['league']['standard']

player_stats_file = open(file_path['player_stats'], 'r')
player_stats_json = json.load(player_stats_file)
player_stats_file.close()


for game in game_list:
	if 'tags' in game and 'PRESEASON' in game['tags']:
		continue
	
	game_date = game['startDateEastern']
	if int(game_date) > 20181111:
		break
	
	game_id = game['gameId']
	print 'processing game:%s ...' % game['gameId']

	box_score_url = '%s/prod/v1/%s/%s_boxscore.json' % (api_base, game_date, game_id)
	
	box_score = requests.get(box_score_url).json()
	active_players = box_score['stats']['activePlayers']
	for player in active_players:
		person_id = player['personId']
		
		if person_id not in player_stats_json:
			player_stats_json[person_id] = {
				'perGame': []
			}

		game_stats = {
			'gameId': game_id
		}
		for key in player:
			if key == 'personId' or key == 'isOnCourt' or key == 'sortKey':
				continue
			game_stats[key] = player[key]
		
		player_stats_json[person_id]['perGame'].append(game_stats)
	
with open(file_path['player_stats'], 'w') as player_stats_file:
	player_stats_file.write(json.dumps(player_stats_json, indent=2))
	player_stats_file.close()
	
	
	
