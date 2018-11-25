import requests
import json
import decimal
import datetime
import sys
import os
import requests
import json
import utils
from shutil import copyfile

api_base = 'http://data.nba.net/10s/'
team_info_path = 'basic_info/team.json' 

team_info = utils.read_json(team_info_path)
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

def update_player_stats(link, file_path, start_date, end_date):
	response = requests.get(link).json()
	game_list = response['league']['standard']
	
	player_stats_file = open(file_path, 'r')
	player_stats_json = json.load(player_stats_file)
	player_stats_file.close()
	
	backup_file(file_path)
	
	for game in game_list:
		if 'tags' in game and 'PRESEASON' in game['tags']:
			continue
	
		game_date = game['startDateEastern']
		if int(game_date) < start_date:
			print 'skip ' + game_date
			continue
		if int(game_date) > end_date:
			print 'break ' + game_date
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
	
		with open(file_path, 'w') as player_stats_file:
			player_stats_file.write(json.dumps(player_stats_json, indent=2))
			player_stats_file.close()

def get_game_in_range(end_date, from_date=20181016, team_id=None):
 response = requests.get(
     'http://data.nba.net/10s/prod/v1/2018/schedule.json').json()
 game_list = response['league']['standard']
 
 query_games = []
 for game in game_list:
  if 'tags' in game and 'PRESEASON' in game['tags']:
   continue

  game_date = game['startDateEastern']
  if int(game_date) < from_date:
   # print 'skip ' + game_date
   continue
  if int(game_date) > end_date:
   # print 'break ' + game_date
   break

  if team_id != None:
   # print json.dumps(game, indent=2)
   if (game['vTeam']['teamId'] != team_id) and (game['hTeam']['teamId'] != team_id):
    continue

  query_games.append(game)

 return query_games			

def gen_game_data(team_key, game_detail):
	team_stats = game_detail['stats'][team_key]['totals']
	for data_key in team_stats:
		if data_key != 'min':
			team_stats[data_key] = float(decimal.Decimal(team_stats[data_key]))
			# print team_stats[data_key]
	
	return {
		'basicInfo': {
			'homeTeam': team_key == 'hTeam'
		},
		'stats': team_stats
	}

def update_db(game_list):
	for game in game_list:
		game_id = game['gameId']
		print 'processing game:%s ...' % game_id
		# ex: http://data.nba.net/10s/prod/v1/20181016/0021800001_boxscore.json
		box_score_url = 'http://data.nba.net/10s/prod/v1/%s/%s_boxscore.json' % (
		game['startDateEastern'], game_id)
		game_detail = requests.get(box_score_url).json()

		# Visit Team
		team_id = game_detail['basicGameData']['vTeam']['teamId']
		update_team_log(team_id, gen_game_data('vTeam', game_detail))
		# Home Team
		team_id = game_detail['basicGameData']['hTeam']['teamId']
		update_team_log(team_id, gen_game_data('hTeam', game_detail))


def update_team_log(team_id, game_data):
	team_info = get_team_info(team_id)
	team_log_file_path = 'team_log/%s.json' % team_info['tricode']
	
	cur_team_log = None
	if os.path.exists(team_log_file_path):
		cur_team_log = utils.read_json(team_log_file_path)
	else:
		cur_team_log = []
	
	cur_team_log.append(game_data)
	utils.write_json(team_log_file_path, cur_team_log)
	
def get_team_info(team_id):
	for team in team_info:
		if team['teamId'] == team_id:
			return team
	raise Exception('Cannot find team with id:%s' % team_id)
			
def get_team_log(team_id, end_date, from_date=20181016):
 game_list = get_game_in_range(end_date, from_date, team_id)

 for game in game_list:
  box_score_url = 'http://data.nba.net/10s/prod/v1/%s/%s_boxscore.json' % (
      game['startDateEastern'], game['gameId'])
  game_detail = requests.get(box_score_url).json()
  # print json.dumps(game_detail, indent=2)

  teamKey = None
  if game_detail['basicGameData']['vTeam']['teamId'] == team_id:
   teamKey = 'vTeam'
  else:
   teamKey = 'hTeam'
  print json.dumps(game_detail['stats'][teamKey]['totals'], indent=2)

  
link_reference_link = api_base + 'prod/v1/today.json'
response = requests.get(link_reference_link).json()

file_path = {
	'roster': 'nba/roster.json',
	'player_stats': 'nba/player_stats.json'
}

#latest_roster = update_roster(api_base + response['links']['leagueRosterPlayers'], file_path['roster'])

#update_player_stats(api_base + response['links']['leagueSchedule'], file_path['player_stats'], 20181114, 20181115)

game_list = get_game_in_range(20181124)
update_db(game_list)
	
	
	
