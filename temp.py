import requests
import json


def get_game_in_range(game_list, end_date, from_date=20181016, team_id=None):
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


def get_team_stats(team_id, end_date, from_date=20181016):
 response = requests.get(
     'http://data.nba.net/10s/prod/v1/2018/schedule.json').json()
 game_list = get_game_in_range(
     response['league']['standard'], end_date, from_date, team_id)

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


# cur_team = []
# for team in response['league']['standard']:
#  if team['isNBAFranchise'] and (not team['isAllStar']):
#   cur_team.append(team)

# with open('team.json', 'w') as player_stats_file:
#  player_stats_file.write(json.dumps(cur_team, indent=2))
#  player_stats_file.close()

get_team_stats('1610612761', 20181116)
