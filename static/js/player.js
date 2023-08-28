const app = Vue.createApp({
    data() {
        return {
            // Flask所傳遞
            myAccount: myAccount,
            accounts: accounts,
            categories: categories,
            fielders: fielders,
            pitchers: pitchers,

            // 決定fielders, pitchers Table的顯示
            fieldersShow: true,
            pitchersShow: true,

            // search, filter資料所使用
            searchName: "",
            statusShow: true,
            statusSelected: "ALL",
            positionShow: true,
            positionSelected: "AB",
            statsShow: true,
            statsSelected: "ST",

            // sortTable使用
            fielderOrder: 1, // 1: 遞增, -1:遞減
            fielderSortCategory: "current",
            pitcherOrder: 1, // 1: 遞增, -1:遞減
            pitcherSortCategory: "current"
        }
    },
    methods: {
        search() {
            this.fieldersShow = false;
            this.fielders.forEach(fielder => {
                if (fielder.name.includes(this.searchName)) {
                    fielder.show = true;
                    this.fieldersShow = true;
                }
                else {
                    fielder.show = false;
                }
            });

            this.pitchersShow = false;
            this.pitchers.forEach(pitcher => {
                if (pitcher.name.includes(this.searchName)) {
                    pitcher.show = true;
                    this.pitchersShow = true;
                }
                else {
                    pitcher.show = false;
                }
            });

            this.statusShow = false;
            this.positionShow = false;

        },
        cancelSearch() {
            this.fielders.forEach(fielder => {
                fielder.show = true;
            });
            this.pitchers.forEach(pitcher => {
                pitcher.show = true;
            });

            this.fieldersShow = true;
            this.pitchersShow = true;

            this.statusShow = true;
            this.statusSelected = "ALL";
            this.positionShow = true;
            this.positionSelected = "AB";
            this.searchName = "";
        },

        filter() {
            // status
            switch (this.statusSelected) {
                case "ALL":
                    this.fielders.forEach(fielder => { fielder.show = true; })
                    this.pitchers.forEach(pitcher => { pitcher.show = true; })
                    break;
                case "FAO":
                    this.fielders.forEach(fielder => {
                        if (!fielder.Account) { fielder.show = true; }
                        else { fielder.show = false; }
                    })
                    this.pitchers.forEach(pitcher => {
                        if (!pitcher.Account) { pitcher.show = true; }
                        else { pitcher.show = false; }
                    })
                    break;
                case "ATP":
                    this.fielders.forEach(fielder => {
                        if (fielder.Account) { fielder.show = true; }
                        else { fielder.show = false; }
                    })
                    this.pitchers.forEach(pitcher => {
                        if (pitcher.Account) { pitcher.show = true; }
                        else { pitcher.show = false; }
                    })
                    break;
                case this.statusSelected:
                    this.fielders.forEach(fielder => {
                        if (fielder.Account == this.statusSelected) { fielder.show = true; }
                        else { fielder.show = false; }
                    })
                    this.pitchers.forEach(pitcher => {
                        if (pitcher.Account == this.statusSelected) { pitcher.show = true; }
                        else { pitcher.show = false; }
                    })
                    break;
            }

            // position
            let fielderPositions = ["C", "1B", "2B", "3B", "SS", "OF"];
            let pitcherPositions = ["SP", "RP"];
            if (this.positionSelected == "AB" || this.positionSelected == "Util") {
                this.fieldersShow = true;
                this.pitchersShow = false;
            }
            else if (this.positionSelected == "AP") {
                this.fieldersShow = false;
                this.pitchersShow = true;
            }
            else if (fielderPositions.includes(this.positionSelected)) {
                this.fieldersShow = true;
                this.pitchersShow = false;

                this.fielders.forEach(fielder => {
                    if (fielder.position.includes(this.positionSelected) && fielder.show) { fielder.show = true; }
                    else { fielder.show = false; }
                });
            }
            else if (pitcherPositions.includes(this.positionSelected)) {
                this.fieldersShow = false;
                this.pitchersShow = true;

                this.pitchers.forEach(pitcher => {
                    if (pitcher.position.includes(this.positionSelected) && pitcher.show) { pitcher.show = true; }
                    else { pitcher.show = false; }
                });
            }
        },
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
        isSelectedCategory(category, type) {
            if (type == "Fielder") {
                return this.categories["S_F"].includes(category);
            }
            else if (type == "Pitcher") {
                return this.categories["S_P"].includes(category);
            }
        },
        sortTable(category, type) {
            if (type == "Fielder") {
                if (this.fielderSortCategory == "current") {
                    if (category == "Rank") {
                        this.fielderOrder *= -1;
                    }
                    else {
                        this.fielderSortCategory = category;
                        this.fielderOrder = -1;
                    }
                }
                else {
                    if (this.fielderSortCategory == category) {
                        this.fielderOrder *= -1;
                    }
                    else if (category == "Rank") {
                        this.fielderSortCategory = "current";
                        this.fielderOrder = 1;
                    }
                    else {
                        this.fielderSortCategory = category;
                        this.fielderOrder = -1;
                    }
                }
                return this.fielders.sort((a, b) => this.fielderOrder * (a[category] - b[category]));
            }
            else if (type == "Pitcher") {
                if (this.pitcherSortCategory == "current") {
                    if (category == "Rank") {
                        this.pitcherOrder *= -1;
                    }
                    else if (["ERA", "WHIP"].includes(category)) {
                        this.pitcherSortCategory = category;
                        this.pitcherOrder = 1;
                    }
                    else {
                        this.pitcherSortCategory = category;
                        this.pitcherOrder = -1;
                    }
                }
                else {
                    if (this.pitcherSortCategory == category) {
                        this.pitcherOrder *= -1;
                    }
                    else if (category == "Rank") {
                        this.pitcherSortCategory = "current";
                        this.pitcherOrder = 1;
                    }
                    else if (["ERA", "WHIP"].includes(category)) {
                        this.pitcherSortCategory = category;
                        this.pitcherOrder = 1;
                    }
                    else {
                        this.pitcherSortCategory = category;
                        this.pitcherOrder = -1;
                    }
                }
                if (category == "SV_H") {
                    return this.pitchers.sort((a, b) => this.pitcherOrder * (a["SV+H"] - b["SV+H"]));
                }
                else if (category == "K9") {
                    return this.pitchers.sort((a, b) => this.pitcherOrder * (a["K/9"] - b["K/9"]));
                }
                else {
                    return this.pitchers.sort((a, b) => this.pitcherOrder * (a[category] - b[category]));
                }
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








// $(document).ready(function () {
//     let searchContainer = $(".searchPlayer")
//     searchContainer.find("form").on("submit", function (event) {
//         event.preventDefault();
//         let searchName = searchContainer.find("#search").val();
//         $.ajax({
//             url: "/player/search?searchName=" + searchName,
//             type: "GET",
//             dataType: "json",
//             success: function (response) {
//                 console.log("update Success");
//             }
//         })
//     })
// })