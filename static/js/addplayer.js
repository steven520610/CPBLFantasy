const app = Vue.createApp({
    data() {
        return {
            // Flask所傳遞
            // 在jinja2內的<script></script>元素內
            // 先宣告要使用的變數
            // 才可以在此處使用
            account: account,
            categories: categories,
            fielders: fielders,
            pitchers: pitchers,
            selectPlayerFA: selectPlayerFA,

            // Vue新增
            fieldersShow: true,
            pitchersShow: true,
            selectPlayerMy: null,
            confirmMessage: null,
            selected: false,
            selectPlayerFAType: "",
            selectPlayerMyType: ""

        }
    },
    computed: {
        imagePathFA() {
            return "../img/player/" + this.selectPlayerFA.name + Number(this.selectPlayerFA.player_id) + ".png";
        },
        imagePathMy() {
            return "../img/player/" + this.selectPlayerMy.name + Number(this.selectPlayerMy.player_id) + ".png";
        },
    },
    methods: {
        addPlayerURL(player) {
            return "https://www.cpbl.com.tw/team/person?Acnt=000000" + player.player_id;
        },
        addPlayerInfo(player) {
            let team;
            switch (player.team) {
                case "中信兄弟":
                    team = "CTB - ";
                    break;
                case "富邦悍將":
                    team = "FG - ";
                    break;
                case "樂天桃猿":
                    team = "RKM - ";
                    break;
                case "味全龍":
                    team = "WD - ";
                    break;
                case "統一7-ELEVEn獅":
                    team = "UL - ";
                    break;
            }
            return team + player.position;
        },
        isFielder(player) {
            if (player.OPS) {
                this.selectPlayerFAType = "Fielder";
                return true;
            }
            else {
                this.selectPlayerFAType = "Pitcher";
                return false;
            }
        },
        isSelectedCategory(category, type) {
            if (type == "Fielder") {
                return this.categories["S_F"].includes(category);
            }
            else if (type == "Pitcher") {
                return this.categories["S_P"].includes(category);
            }
        },
        getCategoryTitle(category) {
            if (category == "SV_H") {
                return "SV+H";
            }
            else if (category == "K9") {
                return "K/9";
            }
            else {
                return category
            }
        },
        dropPlayer(player) {
            this.fielders.forEach(fielder => {
                if (fielder == player) {
                    this.fieldersShow = true;
                    this.pitchersShow = false;
                    this.selectPlayerMyType = "Fielder";

                    fielder.show = true;
                }
                else { fielder.show = false; }
            })

            this.pitchers.forEach(pitcher => {
                if (pitcher == player) {
                    this.fieldersShow = false;
                    this.pitcherShow = true
                    this.selectPlayerMyType = "Pitcher";

                    pitcher.show = true;
                }
                else { pitcher.show = false; }
            })

            this.selectPlayerMy = player;
            this.confirmMessage = "add " + this.selectPlayerFA.name + ", drop " + this.selectPlayerMy.name;
            this.selected = true;
        },
        getCategoryValue(player, category) {
            if (category == "IP") {
                return player[category].toFixed(1);
            }
            if (category == "SV_H") {
                return player["SV+H"];
            }
            else if (category == "K9") {
                return player["K/9"].toFixed(2);
            }
            else if (["AVG", "OBP", "SLG", "OPS"].includes(category)) {
                return player[category].toFixed(3);
            }
            else if (["ERA", "WHIP"].includes(category)) {
                return player[category].toFixed(2);
            }
            return player[category];
        },
    },
    delimiters: ['[[', ']]']
})
app.mount(".app")
