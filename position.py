from sqlalchemy import create_engine, MetaData, Table, Column, text
from modules.config.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db = MetaData()

Fielder = Table("Fielder", db, autoload_with=engine)
Pitcher = Table("Pitcher", db, autoload_with=engine)

# 這邊用手動設定的原因是
# 官網在個人資料上，只會顯示一個守備位置
# 但我想要該球員如果有守過某位置，就增加該守備位置
# (其實可以在守備成績那處理，但我沒寫到，之後再補)

# 以下的順序是照官網所排的球員順序

# 2024.2.17爬時，因為台鋼的球員先跳過後面才處理
# 因此在此處會排在最後
fielder_position_list = [
    "3B",  # 王威晨
    "1B, 3B",  # 王政順
    "SS",  # 江坤宇
    "OF",  # 宋晟睿
    "OF",  # 李聖裕
    "Util",  # 周思齊
    "2B",  # 岳東華
    "OF",  # 岳政華
    "C",  # 林吳晉瑋
    "2B, 3B",  # 林志鋼
    "OF",  # 林書逸
    "1B, 2B, SS, 3B",  # 林瑞鈞
    "1B, 3B",  # 馬鋼
    "C",  # 高宇杰
    "2B, 3B, SS",  # 張仁瑋
    "1B, OF",  # 張志豪
    "1B",  # 許基宏
    "OF",  # 陳子豪
    "OF",  # 陳文杰
    "C",  # 陳家駒
    "1B, OF",  # 曾頌恩
    "1B, 2B, 3B, OF",  # 黃韋盛
    "C",  # 黃鈞聲
    "OF",  # 黃鈞麟
    "OF",  # 詹子賢
    "C",  # 福來喜
    "1B, 2B, 3B, SS, OF",  # 潘志芳
    "1B, 3B",  # 蘇緯達
    "OF",  # 藍寅倫
    "OF",  # 王順和
    "OF",  # 冉承霖
    "1B, 2B, 3B, SS",  # 石翔宇
    "C",  # 全浩瑋
    "C",  # 吉力吉撈・鞏冠
    "2B, 3B",  # 吳東融
    "1B, 2B",  # 吳睿勝
    "Util",  # 李展毅
    "2B",  # 李凱威
    "OF",  # 林孝呈
    "C",  # 林辰勳
    "1B",  # 林智勝
    "OF",  # 邱辰
    "1B, SS, OF",  # 拿莫・伊漾
    "OF",  # 高孝儀
    "2B, SS",  # 張政禹
    "OF",  # 張祐銘
    "1B",  # 張皓緯
    "OF",  # 郭天信
    "OF",  # 陳品捷
    "1B, 2B, 3B, SS",  # 陳思仲
    "OF",  # 曾陶鎔
    "2B, SS",  # 曾傳昇
    "OF",  # 董秉軒
    "1B",  # 瑪仕革斯．俄霸律尼
    "C",  # 劉時豪
    "3B",  # 劉基鴻
    "C",  # 蔣少宏
    "OF",  # 田子杰
    "OF",  # 江亮緯
    "1B, 2B, 3B",  # 何恆佑
    "OF",  # 李丞齡
    "3B",  # 林子豪
    "OF",  # 林安可
    "OF",  # 林佳緯
    "C",  # 林岱安
    "1B",  # 林益全
    "2B, SS",  # 林祖傑
    "1B, 3B, OF",  # 林培緯
    "SS",  # 林靖凱
    "OF",  # 邱智呈
    "1B",  # 姚雨翔
    "OF",  # 施冠宇
    "C",  # 柯育民
    "Util",  # 胡金龍
    "OF",  # 唐肇廷
    "OF",  # 張偉聖
    "C",  # 張翔
    "C",  # 張聖豪
    "2B, 3B, SS",  # 許哲晏
    "1B, 3B",  # 郭阜林
    "C",  # 陳重羽
    "2B",  # 陳重廷
    "OF",  # 陳傑憲
    "1B, 2B, 3B",  # 陳鏞基
    "2B, 3B, SS",  # 黃勇傳
    "2B",  # 楊竣翔
    "1B, 3B",  # 潘傑楷
    "OF",  # 鄭鎧文
    "OF",  # 羅暐捷
    "OF",  # 蘇智傑
    "2B, OF",  # 于森旭
    "OF",  # 孔念恩
    "2B, OF",  # 王正棠
    "1B, 3B",  # 王念好
    "OF",  # 王苡丞
    "SS",  # 王勝偉
    "OF",  # 王詩聰
    "OF",  # 申皓瑋
    "2B, SS",  # 池恩齊
    "3B",  # 李宗賢
    "3B",  # 辛元旭
    "OF",  # 周佳樂
    "2B, SS",  # 林岳谷
    "OF",  # 林哲瑄
    "2B, SS",  # 林澤彬
    "C",  # 姚冠瑋
    "1B",  # 范國宸
    "OF",  # 高國輝
    "1B, OF",  # 高國麟
    "OF",  # 張冠廷
    "C",  # 張進德
    "OF",  # 陳真
    "2B, 3B",  # 楊瑞承
    "2B, SS",  # 葉子霆
    "3B",  # 董子恩
    "C",  # 豊暐
    "OF",  # 廖柏勳
    "2B, SS",  # 劉俊豪
    "OF",  # 蔡佳諺
    "1B",  # 蔣智賢
    "C",  # 蕭憶銘
    "OF",  # 戴云真
    "C",  # 戴培峰
    "C",  # 蘇煒智
    "C",  # 毛英傑
    "OF",  # 成晉
    "1B, OF",  # 朱育賢
    "1B, SS, OF",  # 余德龍
    "C",  # 宋嘉翔
    "2B, SS, OF",  # 林子偉
    "2B, OF",  # 林立
    "3B, SS",  # 林承飛
    "C",  # 林泓育
    "OF",  # 林政華
    "2B, 3B",  # 林智平
    "OF",  # 邱丹
    "2B, 3B, SS",  # 馬傑森
    "C",  # 張閔勛
    "1B, 3B",  # 梁家榮
    "2B, 3B, SS",  # 郭永維
    "1B, 2B, 3B",  # 郭嚴文
    "1B",  # 陳佳樂
    "1B",  # 陳俊秀
    "OF",  # 陳晨威
    "2B, 3B",  # 馮健庭
    "2B",  # 楊晉豪
    "1B",  # 廖健富
    "OF",  # 蔡鎮宇
    "OF",  # 鍾玉成
    "C",  # 顏宏鈞
    "OF",  # 巴奇達魯 妮卡兒
    "1B",  # 王博玄
    "C",  # 吳明鴻
    "C",  # 吳柏萱
    "1B, 3B",  # 杜家明
    "OF",  # 林威漢
    "2B, 3B, SS",  # 林家鋐
    "C",  # 邱邦
    "OF",  # 洪瑋漢
    "2B, 3B",  # 紀慶然
    "2B, SS",  # 胡冠俞
    "OF",  # 孫易伸
    "2B, SS",  # 馬許晧
    "OF",  # 高聖恩
    "SS",  # 張誠恩
    "C",  # 張肇元
    "C",  # 陳世嘉
    "C",  # 陳致嘉
    "2B, SS",  # 陳飛霖
    "SS",  # 曾子祐
    "OF",  # 曾宸佐
    "SS",  # 湯家豪
    "2B, 3B",  # 黃劼希
    "1B, 2B, 3B, SS",  # 黃秉揚
    "OF",  # 葉保弟
    "C",  # 廖奕安
    "1B",  # 顏郁軒
    "OF",  # 顏清浤
]

pitcher_position_list = [
    "RP",  # 王奕凱
    "RP",  # 王凱程
    "RP",  # 江忠城
    "SP",  # 艾士特
    "SP",  # 余謙
    "RP",  # 吳俊偉
    "SP",  # 吳哲源
    "RP",  # 呂彥青
    "RP",  # 李吳永勤
    "RP",  # 李振昌
    "RP",  # 官大元
    "RP",  # 林暉盛
    "RP",  # 徐基麟
    "SP",  # 馬格文
    "RP",  # 張祖恩
    "RP",  # 陳柏豪
    "SP, RP",  # 陳琥
    "RP",  # 彭識穎
    "SP",  # 象魔力
    "RP",  # 黃弘毅
    "SP, RP",  # 楊志龍
    "SP, RP",  # 廖乙忠
    "SP",  # 德保拉
    "RP",  # 蔡齊哲
    "SP",  # 鄭浩均
    "SP",  # 鄭凱文
    "RP",  # 盧孟揚
    "RP",  # 謝榮豪
    "SP, RP",  # 魏碩成
    "SP, RP",  # 王溢正
    "RP",  # 王玉譜
    "SP, RP",  # 王維中
    "RP",  # 王躍霖
    "SP",  # 布里悍
    "SP, RP",  # 伍鐸
    "RP",  # 吳君奕
    "SP",  # 吳俊杰
    "RP",  # 呂偉晟
    "RP",  # 呂詠臻
    "RP",  # 李超
    "SP, RP",  # 林子昱
    "RP",  # 林凱威
    "RP",  # 林逸達
    "SP",  # 徐若熙
    "RP",  # 張景淯
    "SP",  # 曹祐齊
    "RP",  # 莊玉彬
    "SP",  # 郭郁政
    "RP",  # 陳冠偉
    "RP",  # 森榮鴻
    "RP",  # 廖任磊
    "RP",  # 趙璟榮
    "RP",  # 劉昱言
    "RP",  # 劉家愷
    "SP",  # 鋼龍
    "SP",  # 錡龍
    "RP",  # 羅國華
    "RP",  # 羅華韋
    "RP",  # 方建德
    "RP",  # 王鏡銘
    "SP",  # 古林睿煬
    "SP",  # 布萊威
    "SP",  # 布雷克
    "RP",  # 江承峰
    "SP",  # 江承諺
    "RP",  # 江國謙
    "SP",  # 克維斯
    "RP",  # 吳承諭
    "RP",  # 李其峰
    "SP",  # 林子崴
    "RP",  # 林詔恩
    "RP",  # 邱浩鈞
    "SP",  # 姚杰宏
    "SP, RP",  # 施子謙
    "SP",  # 胡智爲
    "RP",  # 陳韻文
    "RP",  # 傅于剛
    "RP",  # 黃竣彥
    "RP",  # 楊孟沅
    "RP",  # 劉予承
    "RP",  # 劉軒荅
    "SP",  # 潘威倫
    "RP",  # 鄭鈞仁
    "SP",  # 羅昂
    "SP",  # 蘭道爾
    "RP",  # 王尉永
    "SP",  # 伍茲
    "SP",  # 江少慶
    "SP",  # 江國豪
    "RP",  # 吳世豪
    "RP",  # 李子強
    "RP",  # 李建勲
    "RP",  # 岳少華
    "SP",  # 肯特
    "SP",  # 恩力
    "SP",  # 郭俊麟
    "SP",  # 陳仕朋
    "RP",  # 陳冠勳
    "RP",  # 陳韋霖
    "RP",  # 陳聖文
    "RP",  # 富藍戈
    "RP",  # 曾峻岳
    "SP",  # 游霆崴
    "RP",  # 黃子宸
    "SP",  # 黃保羅
    "SP",  # 瑞恩
    "RP",  # 歐書誠
    "RP",  # 賴智垣
    "RP",  # 藍愷青
    "SP",  # 羅力
    "RP",  # 王志煊
    "RP",  # 朱俊祥
    "RP",  # 余德龍
    "RP",  # 林子崴
    "RP",  # 林華偉
    "SP",  # 邱駿威
    "SP",  # 威能帝
    "RP",  # 范柏絜
    "RP",  # 張梓軒
    "SP",  # 莊昕諺
    "RP",  # 許峻暘
    "SP",  # 陳克羿
    "RP",  # 陳冠宇
    "RP",  # 陳禹勳
    "RP",  # 陳鴻文
    "SP",  # 曾仁和
    "RP",  # 曾家輝
    "RP",  # 舒治浩
    "SP",  # 黃子鵬
    "RP",  # 黃偉晟
    "SP",  # 楊彬
    "SP",  # 道博格
    "RP",  # 豪勁
    "RP",  # 賴知頎
    "RP",  # 賴鴻誠
    "SP",  # 霍爾
    "RP",  # 蘇俊璋
    "RP",  # 王柏傑
    "SP",  # 王梓安
    "SP",  # 伍祐城
    "RP",  # 巫柏葳
    "RP",  # 李欣穎
    "RP",  # 杜家明
    "RP",  # 林詩翔
    "SP",  # 翁瑋均
    "SP",  # 張喜凱
    "RP",  # 張竣凱
    "RP",  # 許育銘
    "RP",  # 郭俞延
    "RP",  # 陳正毅
    "SP",  # 陳宇宏
    "RP",  # 陳冠豪
    "SP",  # 陳柏清
    "RP",  # 陳翊瑄
    "RP",  # 陳暐皓
    "RP",  # 曾品洋
    "RP",  # 曾奕翔
    "SP",  # 黃勃睿
    "RP",  # 黃紹睿
    "RP",  # 黃群
    "SP",  # 楊達翔
    "SP",  # 福永春吾
    "RP",  # 鄧佳安
    "RP",  # 蕭柏頤
    "RP",  # 謝葆錡
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
