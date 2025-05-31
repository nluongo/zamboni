from zamboni import APICaller

caller = APICaller()
query_out = caller.query("standings", ["2024-12-31"])
print(query_out)
print(query_out["standings"])
for team in query_out["standings"]:
    print(team["teamName"]["default"])
    print(team["teamAbbrev"]["default"])
