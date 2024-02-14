# Modified date: 2024.2.14
# Author: Steven
# Description: 事先定義好在app運行中，不會變動的一些數值

AVG_PA = 250
AVG_AVG = 0.261
AVG_OBP = 0.330
AVG_SLG = 0.365
"""
宣告此專案運行的過程中，不會變動的數值
然而在不同日期內，這些平均的數據可能會有小小的浮動。
"""

# 利用dict的方式
# 指定db內各種數據的column對應到中職網頁中，位於網頁中的第幾個column。
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

# 決定各種數據要如何的計算該球員的分數
# 主要是基於Fantasy上的分數，可以自己做更換。
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
    "W": 10,
    "L": -3,
    "HR": -2,
    "K": 2,
    "BB": -1,
    "HBP": -1,
    "ER": -2,
    "QS": 7,
    # 若利用Flask SQLAlchemy的方式，以class來定義一個table
    # 則每個屬性名稱就是一個column。
    # 然而不能在名稱使用+號(程式語言的規定)，所以該屬性名稱設定為SV_H
    "SV_H": 16,
    "BSV": -5,
}

# 列出成績看板(BOX)中，中職網頁有記錄的數據。
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

# 利用dict的方式
# 將今日有記錄的成績，決定要輸入到db內有記錄今日成績的table中的哪個column
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
