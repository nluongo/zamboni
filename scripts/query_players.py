import requests

#api_id = 8475104
api_id = 8450157
# Less than 2500 players in the league
#end_id = 8477604
end_id = 8500000
fetch_players = 1
step = 1
with open('data/players.txt', 'a') as f:
    while api_id < end_id:
        #if api_id%step != 0:
        #    api_id += 1
        #    continue
        try:
            r = requests.get(f'https://api-web.nhle.com/v1/player/{api_id}/landing')
            player = r.json()
        except:
            if api_id%step == 0:
                print(api_id)
            api_id += 1
            continue
        first_name = player['firstName']['default']
        last_name = player['lastName']['default']
        full_name = f'{first_name} {last_name}'
        print(full_name)
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
