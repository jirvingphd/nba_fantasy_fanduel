# nba_fantasy_fanduel
 
## Task 1:
- Scraping individual player historical data from stats.nba.com/player/__playerid__/boxscores-traditional website

- Want to take today's available players, look up their historical stats at website listed above
- Then want to convert stats to fantasy points 
- Then want to build regression model for predicting today's game's fantasty points per player








### NB STATS COLUMNS GLOSSARY
| COLUMN | MEANING|
| --- | --- |
|W/L|Win/Loss|
|MIN|Minutes Played|
|PTS|Points|
|FGM|Field Goals Made|
|FGA|Field Goals Attempted|
|FG%|Field Goal Percentage|
|3PM|3 Point Field Goals Made|
|3PA|3 Point Field Goals Attempted|
|3P%|3 Point Field Goals Percentage|
|FTM|Free Throws Made|
|FTA|Free Throws Attempted|
|FT%|Free Throw Percentage|
|OREB|Offensive Rebounds|
|DREB|Defensive Rebounds|
|REB|Rebounds|
|AST|Assists|
|STL|Steals|
|BLK|Blocks|
|TOV|Turnovers|
|PF|Personal Fouls|
|+/-|Plus-Minus|

### FANTASY POINT CONVERSIONS

|STAT|PTS|
| --- | --- |
|3PM|1|
|AST| 1.5|
|BLK|3|
|FGM|2|
|FTM|1|
|REB|1.2|
|STL|3|
|TOV|-1|



# WORKFLOW SUMMARY AS OF 12/26/19:

1. Get player's nba_stats id#
2. `import nba_stats as ns`
3. Can directly run `df = ns.get_all_seasons_df(player_id= the_players_id)` (see note below: \$:)
4. `df = ns.calc_fantasy_stats(df)`
5. `ns.save_player_df(df)`

\$: Can instead run helper functions individually if don't want all seasons:
    - `season_urls=ns.make_season_urls_from_playerid`
    - `df = ns.get_season_df(season_url[0])`


Example Below:
```python
import nba_stats as ns
player_id=1628369
df = ns.get_all_seasons_df(player_id=player_id)
df = ns.calc_fantasy_stats(df)
ns.save_player_df(df)
```