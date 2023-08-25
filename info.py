"""
宣告在app中，不會變動的數值
"""

AVG_PA = 250
AVG_AVG = 0.261
AVG_OBP = 0.330
AVG_SLG = 0.365

DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT = {
    "PA": 1,
    "AB": 2,
    "RBI": 3,
    "R": 4,
    "H": 5,
    "1H": 6,
    "2H": 7,
    "3H": 8,
    "HR": 9,
    "TB": 10,
    "K": 11,
    "SB": 12,
    "OBP": 13,
    "SLG": 14,
    "AVG": 15,
    "DP": 16,
    "BUNT": 17,
    "SF": 18,
    "BB": 19,
    "IBB": 20,
    "HBP": 21,
    "CS": 22,
    "OPS": 27,
}
DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT = {
    "APP": 0,
    "W": 6,
    "L": 7,
    "SV": 8,
    "BSV": 9,
    "HLD": 10,
    "SV+H": [8, 10],
    "IP": 11,
    "WHIP": 12,
    "ERA": 13,
    "H": 16,
    "HR": 17,
    "BB": 18,
    "HBP": 20,
    "K": 21,
    "R": 24,
    "ER": 25,
}

SCORING_FIELDER = {
    "R": 3,
    "RBI": 3,
    "H1": 3,
    "H2": 4,
    "H3": 5,
    "HR": 6,
    "TB": 1,
    "K": -1.5,
    "BB": 2.5,
    "IBB": 1.5,
    "HBP": 1.5,
    "SB": 5,
    "CS": -2.5,
}
SCORING_PITCHER = {
    "APP": 2,
    "IP": 3.6,
    "W": 10,
    "L": -3,
    "HR": -2,
    "K": 2,
    "BB": -1,
    "HBP": -1,
    "ER": -2,
    "QS": 7,
    # 因為是用Flask SQLAlchemy的class
    # 因為不能在名稱使用+號，所以該屬性設定為SV_H
    # 而isinstance檢查的是class，不是db內的欄位名稱
    # 所以這邊要使用SV_H
    "SV_H": 16,
    "BSV": -5,
}

BOX_TITLE_FIELDER = [
    "AB",
    "R",
    "H",
    "RBI",
    "2H",
    "3H",
    "HR",
    "DP",
    "BB",
    "IBB",
    "HBP",
    "K",
    "BUNT",
    "SF",
    "SB",
    "CS",
]
BOX_TITLE_PITCHER = [
    "IP",
    "H",
    "HR",
    "BB",
    "HBP",
    "K",
    "R",
    "ER",
]

FIELDER_CATEGORIES_TO_TODAY_CATEGORIES = {
    "PA": 3,
    "AB": 4,
    "R": 5,
    "RBI": 6,
    "H": 7,
    # 沒有1H
    "2H": 8,
    "3H": 9,
    "HR": 10,
    "TB": 11,
    "DP": 12,
    "BB": 13,
    "IBB": 14,
    "HBP": 15,
    "K": 16,
    "SF": 17,
    "BUNT": 18,
    "SB": 19,
    "CS": 20,
    "AVG": 21,
    "OBP": 22,
    "SLG": 23,
    "OPS": 24,
}
PITCHER_CATEGORIES_TO_TODAY_CATEGORIES = {
    "IP": 3,
    "W": 4,
    "L": 5,
    "H": 6,
    "HR": 7,
    "BB": 8,
    "HBP": 9,
    "K": 10,
    "R": 11,
    "ER": 12,
    "ERA": 13,
    "WHIP": 14,
    "K9": 15,
    "QS": 16,
    "HLD": 17,
    "SV": 18,
    "SV_H": 19,
    "BSV": 20,
}


def read_category():
    """讀取categories.txt內的比項

    Returns:
        list: fielder_categories,
        list: pitcher_categories,
        int: number of fielder_categories,
        int: number of pitcher_categories
    """
    fielder_categories, pitcher_categories = [], []
    path = "categories.txt"
    with open(path, "r") as file:
        index = 0
        for line in file.readlines():
            if line.strip() != "-":
                index += 1
            else:
                split_index = index
    with open(path, "r") as file:
        lines = file.readlines()
        for i in range(1, split_index):
            fielder_categories.append(lines[i].strip())
        for i in range(split_index + 2, len(lines)):
            pitcher_categories.append(lines[i].strip())
    return (
        fielder_categories,
        pitcher_categories,
        len(fielder_categories),
        len(pitcher_categories),
    )
