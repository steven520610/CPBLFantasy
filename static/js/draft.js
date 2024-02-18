// 排序
function sortTable(n, direction) {
    let table, rows, i, r1, r2, switching, shouldSwitch, switchCount, allZero;
    table = document.getElementsByTagName("table")[1]
    switching = true;
    switchCount = 0
    rows = table.rows;
    allZero = true;

    for (i = 1; i < (rows.length) - 1; i++) {
        if (Number(rows[i].getElementsByTagName("td")[n].innerHTML) != (0 || "")) {
            allZero = false;
            break;
        }
    }


    while (switching) {
        if (allZero) {
            break;
        }
        switching = false;
        rows = table.rows;
        // 利用類似Bubble Sort的流程
        for (i = 1; i < (rows.length) - 1; i++) {
            r1 = Number(rows[i].getElementsByTagName("td")[n].innerHTML);
            r2 = Number(rows[i + 1].getElementsByTagName("td")[n].innerHTML);
            if (direction == "asc" && r1 > r2) {
                shouldSwitch = true;
                break;
            }
            else if (direction == "desc" && r1 < r2) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch && i < (rows.length - 1)) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchCount++;
        }
        else {
            if (switchCount == 0 && direction == "asc") {
                direction = "desc";
                switching = true;
            }
            else if (switchCount == 0 && direction == "desc") {
                direction = "asc";
                switching = true;
            }
        }
    }
}

// 資源載入完成
$(document).ready(function () {
    // 在資源都加載完成後就先宣告WebSocket
    // 因為此JS檔，是專門給draft.html使用的，也就是說這個檔案只會和/draft這個路由有關
    // 因此宣告socket時，就直接在最後加上namespace
    // 如此就不需要發送事件給預設(所有伺服器端的路由)，只會發送給/draft，可以減少一些資源
    // 在Flask端也需要做設定
    const socket = io("http://127.0.0.1:5000/draft");

    // server端不用新增一個socket.emit("connect")來處理
    // 這是只要server回覆一個response(連線成功)，就會執行的callback
    socket.on("connect", function () {
        console.log("Connected to Server!");
    });

    let rounds, round, orders, order, i, j, login, allP, allMe, playerData;
    const rankList = [];

    //#region 處理整個網頁在選秀時都不會變動的部分

    titleName = {}
    // thead中的tr的第一欄，不像tbody中的tr第一欄為playerID，所以這邊手動assign
    titleName["0"] = "player_ID";
    heads = $("#playersTable thead tr").children();
    // flag用來區分目前是batter or pitcher
    // false -> batter
    // true -> pitcher
    let flag = false;
    for (i = 0; i < heads.length; i++) {
        if (heads.eq(i).text() == "IP") flag = true;
        if (heads.eq(i).text() == "HR" && !flag) titleName[i + 1] = "HR_fielder";
        else if (heads.eq(i).text() == "K" && !flag) titleName[i + 1] = "K_fielder";
        else if (heads.eq(i).text() == "BB" && !flag) titleName[i + 1] = "BB_fielder";
        else if (heads.eq(i).text() == "HR" && flag) titleName[i + 1] = "HR_pitcher";
        else if (heads.eq(i).text() == "K" && flag) titleName[i + 1] = "K_pitcher";
        else if (heads.eq(i).text() == "BB" && flag) titleName[i + 1] = "BB_pitcher";
        else titleName[i + 1] = heads.eq(i).text();
    }
    let totalPicks = Number($(".order").last().text());
    let totalPlayers = Number($(".round").first().children().length);
    let totalRounds = Math.floor(totalPicks / totalPlayers);
    let currentRound, currentPick, currentOverall;
    let count = 0;
    //#endregion


    //#region 處理一加載完網頁，就需要優先加上的CSS。
    // 像是playersTable的第一列、account bar的第一個玩家

    // 每個user進來都會先自動選取第一列
    $("#playersTable tbody").children().first().addClass("selected");

    // 每個user進來都可以清楚看到第一個pick的人是誰以及順位是多少
    $(".round").first().children().first().addClass("turn");
    login = $("#login").text();

    // 每個user進來，預設都會先顯示Players table
    $("#teamsTable").css("display", "none");
    $("#draftResultsTable").css("display", "none");
    $("#standingsTable").css("display", "none");

    let playersHead = $("#playersTable thead tr");
    let selected = $(".selected");
    let showHead = $("#showHead");
    let showBody = $("#showBody");
    for (let i = 0; i < 11; i++) {
        // 若為投手，該欄位會是empty
        // 若為打者，該欄位會是PA
        if (selected.children().eq(3).text()) {
            // Head為i+2, Body為i+3的原因是
            // Body多了第一欄位的playerID
            showHead.children().eq(i + 1).text(playersHead.children().eq(i + 2).text());
            showBody.children().eq(i + 1).text(selected.children().eq(i + 3).text());
        }
        else {
            showHead.children().eq(i + 1).text(playersHead.children().eq(i + 13).text());
            showBody.children().eq(i + 1).text(selected.children().eq(i + 14).text());
        }
    }
    //#endregion


    //#region 處理不同帳號登入選秀頁面後，在account bar的CSS
    rounds = $(".round");
    // 標示出每一輪中，自己位於哪一個選秀順位
    for (i = 0; i < rounds.length; i++) {
        round = rounds.eq(i);
        orders = round.children();
        for (j = 0; j < orders.length; j++) {
            order = orders.eq(j);
            if (order.children().eq(2).text() == login) {
                order.addClass("me");
            }
        }
    }
    //#endregion

    // 選秀開始前
    $("#turnIndicator").addClass("clockNotMyTurn");
    $("#turnIndicator").text("The draft will start soon.");

    // 發送jQuery的簡化版AJAX請求
    // 目標是從server端取得選秀時間
    let startTime, remainSecond, remainMinute;
    $.getJSON("/draft/time", function (data) {
        const time = new Date(data.Time);
        startTime = time.getTime();
        const current = new Date();
        remainSecond = Math.floor((startTime - current.getTime()) / 1000);
        remainMinute = Math.floor(remainSecond / 60);
    });


    // 處理計時器的部分
    let startTimer, draftTimer;

    // 選秀開始前的計時器
    startTimer = setInterval(function () {
        if (remainSecond > 0) {
            remainSecond--;
            if ((remainSecond % 60) < 10) {
                showTime = remainMinute + ":" + "0" + remainSecond % 60;
            }
            else {
                showTime = remainMinute + ":" + remainSecond % 60;
            }
            if (!(remainSecond % 60)) { remainMinute--; }

            $("#timer").text(showTime);
        }
        // 時間到時，觸發第一個計時器
        else {
            clearInterval(startTimer);
            socket.emit("firstTimer", true);
            console.log("firstTimer已發出！");
        }
    }, 1000);

    // 選秀時的計時器
    let updateTimer = function (data) {
        // 每次開始新的計時器前
        // 先清除此處的上一個計時器
        clearInterval(draftTimer);
        // 處理每次啟動計時器時
        // 左側account bar的CSS
        allP = $("p");
        allMe = $(".me");
        if ($(".turn.me").length) {
            $("#turnIndicator").removeClass("clockNotMyTurn");
            $("#turnIndicator").addClass("clockMyTurn");
            $("#turnIndicator").text("It's your turn to draft!");
            $("#draft").css("visibility", "visible");
        }
        else {
            let nextMe = allP.index(allMe.first());
            $("#turnIndicator").removeClass("clockMyTurn");
            $("#turnIndicator").addClass("clockNotMyTurn");
            $("#turnIndicator").text(nextMe + " picks until your turn");
            $("#draft").css("visibility", "hidden");
        }

        // 啟動計時器
        $("#timer").text("1:00");
        let remain = 60;
        draftTimer = setInterval(function () {
            if (remain > 0) {
                remain--;
                if (remain < 10) {
                    $("#timer").text("0:0" + remain);
                }
                else {
                    $("#timer").text("0:" + remain);
                }
            }
            // 使用者未在時間內選擇時
            // 會自動選擇最上面(Rank最高)的球員
            else {
                clearInterval(draftTimer);
                // 當下的user送出update即可
                if ($(".account").first().text() == login) {
                    playerData = {};
                    row = $("#playersTable tbody").children().first();
                    columns = row.children();
                    for (i = 0; i < columns.length; i++) {
                        playerData[titleName[i]] = columns.eq(i).text();
                    }
                    playerData["Account"] = login;
                    playerData["round"] = Math.floor((Number($(".order").first().text()) - 1) / (totalPicks / totalRounds)) + 1;
                    playerData["auto"] = true;
                    rankList.push(playerData["Rank"]);
                    socket.emit("update", playerData);
                    socket.emit("draftTimer", playerData["auto"]);
                }
            }
        }, 1000);
    }
    socket.on("firstTimer", updateTimer);
    socket.on("draftTimer", updateTimer);

    // 點擊Players_table的表頭
    $("#playersTable th").click(function () {
        let n = $(this).index();
        // console.log(n)
        switch (n + 1) {
            case 1:
                sortTable(n + 1, "asc");
                break;
            case 2:
                break;
            case 18:
                sortTable(n + 1, "asc");
                break;
            case 19:
                sortTable(n + 1, "asc");
                break;
            default:
                sortTable(n + 1, "desc");
        }
        $("tr.selected").removeClass("selected");
        let first = $("#playersTable tbody tr").first();
        first.addClass("selected");
        let name = encodeURIComponent(first.children(".playerName").text());
        let id = first.children(".playerID").text();
        $("#playerImg").attr("src", "/img/player/" + name + id + ".png");

        $("#playerInfoBar .name").text(first.children(".playerName").text());
        let dataContent = first.children(".playerName").attr("data-content");
        dataContent = dataContent.trim().split(" - ");
        $("#playerInfoBar .info").text(dataContent[1] + " | " + dataContent[0]);

        for (let i = 0; i < 11; i++) {
            if (first.children().eq(3).text()) {
                showHead.children().eq(i + 1).text(playersHead.children().eq(i + 2).text());
                showBody.children().eq(i + 1).text(first.children().eq(i + 3).text());
            }
            else {
                showHead.children().eq(i + 1).text(playersHead.children().eq(i + 13).text());
                showBody.children().eq(i + 1).text(first.children().eq(i + 14).text());
            }
        }
    });


    // 處理表格內的球員列中被選取後的反白
    // 以及選取後網頁上方球員照片的顯示
    $("#playersTable tbody tr").click(function () {
        $("tbody tr").removeClass("selected");
        let selected = $(this);
        selected.addClass("selected");
        let name = encodeURIComponent(selected.children(".playerName").text());
        let id = selected.children(".playerID").text();
        $("#playerImg").attr("src", "/img/player/" + name + id + ".png");

        $("#playerInfoBar .name").text(selected.children(".playerName").text());
        let dataContent = selected.children(".playerName").attr("data-content");
        dataContent = dataContent.trim().split(" - ");
        $("#playerInfoBar .info").text(dataContent[1] + " | " + dataContent[0]);

        for (let i = 0; i < 11; i++) {
            if (selected.children().eq(3).text()) {
                showHead.children().eq(i + 1).text(playersHead.children().eq(i + 2).text());
                showBody.children().eq(i + 1).text(selected.children().eq(i + 3).text());
            }
            else {
                showHead.children().eq(i + 1).text(playersHead.children().eq(i + 13).text());
                showBody.children().eq(i + 1).text(selected.children().eq(i + 14).text());
            }
        }
    });

    // ** 處理選擇球員後，按下按鈕送出的地方 **

    $("#draft").click(function () {
        // 每次按下按鈕，都要清除正在計數的計時器
        clearInterval(draftTimer);

        playerData = {};
        let row = $(".selected");
        for (let i = 0; i < row.children().length; i++) {
            playerData[titleName[i]] = row.children().eq(i).text();
        }
        playerData["Account"] = login;
        playerData["round"] = Math.floor((Number($(".order").first().text()) - 1) / (totalPicks / totalRounds)) + 1;
        playerData["auto"] = false;
        rankList.push(playerData["Rank"]);

        // 發送update事件訊息給server端
        socket.emit("update", playerData);
        // 更新計時器
        socket.emit("draftTimer", playerData["auto"]);

        // 最後一個玩家選擇完，要通知後端進行一次rearrange
        // 否則選秀完，沒重開的話，到myteam, matchup會沒東西
        if (currentOverall == totalPicks) {
            socket.emit("rearrange", true);
        }
    });
    //#endregion


    // 接收update事件從server端傳回來的訊息
    socket.on("update", function (backData) {
        // 沒收到伺服器端傳回來的update事件，直接結束
        if (backData["message"] != "Success!") {
            return
        }
        let selectedRow, selectedRowID, next, name, id;
        selectedRow = $(".selected");
        selectedRowID = selectedRow.children().first().text();

        // 回傳回來的資料
        // 依照自動選擇、user選擇
        // 有不同的處理方法
        if (backData["auto"]) {
            $("#playersTable tbody tr").first().remove();
            if (backData["player_ID"] == selectedRowID) {
                next = $("tbody tr").first();
                next.addClass("selected");
                name = encodeURIComponent(next.children(".playerName").text());
                id = next.children(".playerID").text();
                $("#playerImg").attr("src", "/img/player/" + name + id + ".png");
                $("#playerInfoBar .name").text(next.children(".playerName").text());
                let dataContent = next.children(".playerName").attr("data-content");
                dataContent = dataContent.trim().split(" - ");
                $("#playerInfoBar .info").text(dataContent[1] + " | " + dataContent[0]);

                for (let i = 0; i < 11; i++) {
                    if (next.children().eq(3).text()) {
                        showHead.children().eq(i + 1).text(playersHead.children().eq(i + 2).text());
                        showBody.children().eq(i + 1).text(next.children().eq(i + 3).text());
                    }
                    else {
                        showHead.children().eq(i + 1).text(playersHead.children().eq(i + 13).text());
                        showBody.children().eq(i + 1).text(next.children().eq(i + 14).text());
                    }
                }
            }
        }
        else {
            let findId;
            let rows = $("#playersTable tbody tr");
            for (i = 0; i < rows.length; i++) {
                findId = rows.eq(i).children().first().text();
                if (findId == backData["player_ID"]) {
                    // 不是當順位的user中，如果當下所選(反白)的球員被選走的情況
                    // 當順位的user一定會成立(因為按鈕按下時，一定是選selected的，和送出的球員相同)
                    if (selectedRowID == backData["player_ID"]) {
                        if (i != rows.length - 1) {
                            next = rows.eq(i).next();
                        }
                        else {
                            next = rows.eq(i).prev();
                        }
                        next.addClass("selected");
                        name = encodeURIComponent(next.children(".playerName").text());
                        id = next.children(".playerID").text();
                        $("#playerImg").attr("src", "/img/player/" + name + id + ".png");
                        $("#playerInfoBar .name").text(next.children(".playerName").text());
                        let dataContent = next.children(".playerName").attr("data-content");
                        dataContent = dataContent.trim().split(" - ");
                        $("#playerInfoBar .info").text(dataContent[1] + " | " + dataContent[0]);

                        for (let j = 0; j < 11; j++) {
                            if (next.children().eq(3).text()) {
                                showHead.children().eq(j + 1).text(playersHead.children().eq(j + 2).text());
                                showBody.children().eq(j + 1).text(next.children().eq(j + 3).text());
                            }
                            else {
                                showHead.children().eq(j + 1).text(playersHead.children().eq(j + 13).text());
                                showBody.children().eq(j + 1).text(next.children().eq(j + 14).text());
                            }
                        }
                    }
                    rows.eq(i).remove();
                    break;
                }
            }
        }

        // 處理每輪、每個順位，左側account bar的CSS
        let currentAccount = $(".turn");
        if (currentAccount.next().length) {
            currentAccount.next().addClass("turn");
            currentAccount.remove()
        }
        else {
            currentAccount.parent().remove();
            $(".line").first().remove();
            // $(".roundSeperator").first().remove();
            $(".round").first().children().first().addClass("turn");
        }

        // 處理每輪、每個順位，左上角的輪次順位說明
        currentRound = Math.floor((Number($(".order").first().text()) - 1) / totalPlayers) + 1;
        $(".clockRound").text("Round " + currentRound);

        currentPick = $(".round").first().children().length;
        $(".clockPick").text("Pick " + totalPlayers - currentPick + 1);

        currentOverall = Number($(".order").first().text());
        switch (currentOverall % 10) {
            case 1:
                $("#clockOverall").text(currentOverall + "st Overall");
                break;
            case 2:
                $("#clockOverall").text(currentOverall + "nd Overall");
                break;
            case 3:
                $("#clockOverall").text(currentOverall + "rd Overall");
                break;
            default:
                $("#clockOverall").text(currentOverall + "th Overall");
        }
    });

    // 處理導引到四個不同表格的按鈕
    for (let i = 0; i < 4; i++) {
        $("#rightButton").children().eq(i).click(function () {
            $("#rightButton").children().removeClass("selected");
            $("#rightButton").children().eq(i).addClass("selected");
            if (i == 0) {
                $("#bodyRight").children().eq(1).css("display", "block");
                $("#bodyRight").children().eq(2).css("display", "none");
                $("#bodyRight").children().eq(3).css("display", "none");
                $("#bodyRight").children().eq(4).css("display", "none");
            }
            else if (i == 1) {
                $("#bodyRight").children().eq(1).css("display", "none");
                $("#bodyRight").children().eq(2).css("display", "block");
                $("#bodyRight").children().eq(3).css("display", "none");
                $("#bodyRight").children().eq(4).css("display", "none");
            }
            else if (i == 2) {
                $("#bodyRight").children().eq(1).css("display", "none");
                $("#bodyRight").children().eq(2).css("display", "none");
                $("#bodyRight").children().eq(3).css("display", "block");
                $("#bodyRight").children().eq(4).css("display", "none");
            }
            else {
                $("#bodyRight").children().eq(1).css("display", "none");
                $("#bodyRight").children().eq(2).css("display", "none");
                $("#bodyRight").children().eq(3).css("display", "none");
                $("#bodyRight").children().eq(4).css("display", "block");
            }
        });
    }

    // 點擊Teams按鈕
    $("#rightButton").children().eq(1).click(function () {
        let login_json = { "login": login };
        $.ajax({
            url: "/draft/teams",
            type: "POST",
            data: JSON.stringify(login_json),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                if (!playerData) return;
                returnData = response["data"];
                fielder_stats = response["stats"][0];
                pitcher_stats = response["stats"][1];

                fieldersData = returnData["fielders"];
                pitchersData = returnData["pitchers"];

                fielderRows = $("#teamsTable tbody").eq(0).children();
                pitcherRows = $("#teamsTable tbody").eq(1).children();

                let fielderBn = 11;
                let pitcherBn = 8;

                let nextLoop = false;

                for (let i = 0; i < fieldersData.length; i++) {
                    let fielder = fieldersData[i];
                    $("#teamsTable .playerName").each(function () {
                        if ($(this).text() == fielder["Player"]) {
                            nextLoop = true;
                        }
                    })
                    if (nextLoop) {
                        nextLoop = false;
                        continue;
                    }
                    let playerAdd = false;
                    let position = fielder["position"];
                    for (let j = 0; j < position.length; j++) {
                        for (let k = 0; k < fielderRows.length; k++) {
                            if (((position[j] == fielderRows.eq(k).children().first().text()) && fielderRows.eq(k).children().eq(1).text() == "")) {
                                fielderRows.eq(k).children().eq(1).text(fielder["Player"]);
                                fielderRows.eq(k).children().eq(2).text(rankList[fielder["round"] - 1]);
                                fielderRows.eq(k).children().eq(3).text(fielder["PA"]);
                                fielderRows.eq(k).children().eq(4).text(fielder["AB"]);
                                for (let z = 0; z < fielder_stats.length; z++) {
                                    fielderRows.eq(k).children().eq(z + 5).text(fielder[fielder_stats[z]]);
                                }
                                playerAdd = true;
                                break;
                            }
                        }
                        if (playerAdd) break;
                    }
                    if (!playerAdd) {
                        fielderRows.eq(fielderBn).children().eq(1).text(fielder["Player"]);
                        fielderRows.eq(fielderBn).children().eq(2).text(rankList[[fielder["round"] - 1]]);
                        fielderRows.eq(fielderBn).children().eq(3).text(fielder["PA"]);
                        fielderRows.eq(fielderBn).children().eq(4).text(fielder["AB"]);
                        for (let z = 0; z < fielder_stats.length; z++) {
                            fielderRows.eq(fielderBn).children().eq(z + 5).text(fielder[fielder_stats[z]]);
                        }
                        fielderBn++;
                    }
                }

                for (let i = 0; i < pitchersData.length; i++) {
                    let pitcher = pitchersData[i];
                    $("#teamsTable .playerName").each(function () {
                        if ($(this).text() == pitcher["Player"]) {
                            nextLoop = true;
                        }
                    })
                    if (nextLoop) {
                        nextLoop = false;
                        continue;
                    }
                    let playerAdd = false;
                    let position = pitcher["position"];

                    for (let j = 0; j < position.length; j++) {
                        for (let k = 0; k < pitcherRows.length; k++) {
                            if (position[j] == pitcherRows.eq(k).children().first().text() && pitcherRows.eq(k).children().eq(1).text() == "") {
                                pitcherRows.eq(k).children().eq(1).text(pitcher["Player"]);
                                pitcherRows.eq(k).children().eq(2).text(rankList[[pitcher["round"] - 1]]);
                                for (let z = 0; z < pitcher_stats.length; z++) {
                                    pitcherRows.eq(k).children().eq(z + 3).text(pitcher[pitcher_stats[z]]);
                                }
                                playerAdd = true;
                                break;
                            }
                        }
                        if (playerAdd) break;
                    }
                    if (!playerAdd) {
                        pitcherRows.eq(pitcherBn).children().eq(1).text(pitcher["Player"]);
                        pitcherRows.eq(pitcherBn).children().eq(2).text(rankList[[pitcher["round"] - 1]]);
                        for (let z = 0; z < pitcher_stats.length; z++) {
                            pitcherRows.eq(pitcherBn).children().eq(z + 3).text(pitcher[pitcher_stats[z]]);
                        }
                        pitcherBn++;
                    }
                }

                for (let i = 0; i < fieldersData.length; i++) {
                    let fielder = fieldersData[i];
                    for (let j = 0; j < fielderRows.length; j++) {
                        if (fielder["Player"] == fielderRows.eq(j).children().eq(1).text()) {
                            let content = "";
                            switch (fielder["team"]) {
                                case "中信兄弟":
                                    content += " CTB - ";
                                    break;
                                case "樂天桃猿":
                                    content += " RKM - ";
                                    break;
                                case "味全龍":
                                    content += " WD - ";
                                    break;
                                case "富邦悍將":
                                    content += " FG - ";
                                    break;
                                default:
                                    content += " UL - ";
                            }
                            let position = "";
                            for (let k = 0; k < fielder["position"].length; k++) {
                                position += fielder["position"][k];
                                if (k != fielder["position"].length - 1) {
                                    position += ", ";
                                }
                            }
                            fielderRows.eq(j).children().eq(1).attr("data-content", content + position);
                        }
                    }
                }

                for (let i = 0; i < pitchersData.length; i++) {
                    let pitcher = pitchersData[i];
                    for (let j = 0; j < pitcherRows.length; j++) {
                        if (pitcher["Player"] == pitcherRows.eq(j).children().eq(1).text()) {
                            let content = "";
                            switch (pitcher["team"]) {
                                case "中信兄弟":
                                    content += " CTB - ";
                                    break;
                                case "樂天桃猿":
                                    content += " RKM - ";
                                    break;
                                case "味全龍":
                                    content += " WD - ";
                                    break;
                                case "富邦悍將":
                                    content += " FG - ";
                                    break;
                                default:
                                    content += " UG - ";
                            }
                            pitcherRows.eq(j).children().eq(1).attr("data-content", content + pitcher["position"]);
                        }
                    }
                }
            },
            error: function (jqXHR) {
                console.log(jqXHR.status);
            }
        });
    });

});