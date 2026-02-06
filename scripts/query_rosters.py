from zamboni import APICaller

caller = APICaller('roster')

team_abbrev = 'EDM'
start_year = 1979
end_year = 1980

api_ids = [team_abbrev, start_year, end_year]

out = caller.query(api_ids)

for forward in out['forwards']:
    print(forward)
