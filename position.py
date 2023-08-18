from sqlalchemy import create_engine, MetaData, Table, Column, text
from config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db = MetaData()

Fielder = Table("Fielder", db, autoload_with=engine)
Pitcher = Table("Pitcher", db, autoload_with=engine)

fielder_position_list = [
    "3B",
    "1B, 3B",
    "SS",
    "OF",
    "OF",
    "Util",
    "2B",
    "OF",
    "C",
    "2B, 3B, SS, OF",
    "OF",
    "1B, 3B",
    "C",
    "2B, 3B, SS",
    "1B, OF",
    "1B",
    "OF",
    "OF",
    "C",
    "1B, OF",
    "1B, 2B, 3B, OF",
    "C",
    "OF",
    "C",
    "1B, 2B, 3B, SS, OF",
    "1B, 3B",
    "OF",
    "OF",
    "1B, 3B, SS",
    "C",
    "2B, 3B",
    "2B",
    "2B",
    "OF",
    "C",
    "1B",
    "OF",
    "1B, SS, OF",
    "OF",
    "2B, SS",
    "OF",
    "1B",
    "OF",
    "OF",
    "OF",
    "SS",
    "OF",
    "1B",
    "C",
    "3B",
    "C",
    "OF",
    "OF",
    "1B, 2B, 3B",
    "OF",
    "3B",
    "OF",
    "C",
    "1B",
    "2B, SS",
    "SS",
    "OF",
    "1B",
    "OF",
    "C",
    "Util",
    "OF",
    "OF",
    "C",
    "2B, SS",
    "1B, 3B",
    "C",
    "2B",
    "OF",
    "1B, 2B, 3B",
    "2B",
    "1B, 3B",
    "OF",
    "OF",
    "OF",
    "OF",
    "2B, OF",
    "1B",
    "SS",
    "OF",
    "OF",
    "2B, SS",
    "3B",
    "3B",
    "OF",
    "2B",
    "OF",
    "2B, SS",
    "C",
    "1B",
    "OF",
    "1B, OF",
    "OF",
    "C",
    "OF",
    "2B, 3B",
    "2B, SS",
    "OF",
    "2B, SS",
    "OF",
    "1B",
    "C",
    "OF",
    "C",
    "C",
    "OF",
    "1B, OF",
    "1B, SS, OF",
    "C",
    "2B, OF",
    "3B, SS",
    "C",
    "OF",
    "2B, 3B",
    "OF",
    "2B, 3B, SS",
    "C",
    "1B, 3B",
    "2B, 3B, SS",
    "1B, 2B, 3B",
    "1B",
    "OF",
    "2B, 3B",
    "2B",
    "1B",
    "OF",
    "OF",
    "C",
]

pitcher_position_list = [
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP",
    "SP, RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "SP",
    "SP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP",
    "SP",
    "RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP, RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP",
    "SP",
    "SP",
    "SP",
    "RP",
    "SP",
    "RP",
    "RP",
    "SP",
    "SP, RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "RP",
    "SP, RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
    "SP",
    "RP",
    "RP",
    "SP, RP",
    "RP",
    "SP",
    "RP",
    "RP",
    "RP",
    "SP",
    "SP",
    "RP",
    "SP, RP",
    "SP",
    "SP",
    "RP",
    "RP",
    "RP",
    "SP",
    "RP",
]
with engine.begin() as connection:
    select_fielders = "SELECT * FROM Fielder"
    fielders = connection.execute(text(select_fielders))
    i = 0
    for fielder in fielders:
        update_statement = (
            "UPDATE Fielder SET position = '{}' WHERE player_id = {}".format(
                fielder_position_list[i], fielder[1]
            )
        )
        connection.execute(text(update_statement))
        i += 1

    i = 0
    select_pitchers = "SELECT * FROM Pitcher"
    pitchers = connection.execute(text(select_pitchers))
    for pitcher in pitchers:
        update_statement = (
            "UPDATE Pitcher SET position = '{}' WHERE player_id = {}".format(
                pitcher_position_list[i], pitcher[1]
            )
        )
        connection.execute(text(update_statement))
        i += 1
