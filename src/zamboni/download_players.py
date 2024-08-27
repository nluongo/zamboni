import requests
from zamboni import APICaller

caller = APICaller('player')

#api_id = 8475104
api_id = 8450157
# Less than 2500 players in the league
#end_id = 8477604
end_id = 8500000
fetch_players = 1
step = 1
with open('data/players.txt', 'a') as f:
    while api_id < end_id:
        player = caller.query(api_id, throw_error=False)
        if not player:
            if api_id%step == 0:
                print(api_id)
            api_id += 1
            continue
        first_name = player['firstName']['default']
        last_name = player['lastName']['default']
        full_name = f'{first_name} {last_name}'
        if 'sweaterNumber' not in player.keys():
            number = '-1'
        else:
            number = str(player['sweaterNumber'])
        if 'position' not in player.keys():
            position = 'U'
        else:
            position = player['position']
        write_string = ','.join([str(api_id), full_name, first_name, last_name, number, position])
        f.write(write_string+'\n')
        api_id += 1
