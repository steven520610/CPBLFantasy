$(document).ready(function () {
    const date = new Date();
    dateString = date.toLocaleDateString();
    // dateString = dateString.slice(0, 10);
    $("#date h1").text(dateString);

    const socket = io("http://127.0.0.1:5000/myteam");
    socket.on("connect", function () {
        console.log("Connect!");
    });
    let account = $("#message").attr("value");


    //  進入網頁後，先宣告的變數，分別有
    //  Fielder, Pitcher在db內的所有欄位
    let fielderCategoriesAll = $("#fielderTable thead th");
    // [position, type, 'PA', 'AB', 'R', 'RBI', 'H', '2H', '3H', 'HR', 'TB', 'DP', 'BB', 'IBB', 'HBP', 'K', 'SF', 'BUNT', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS', empty]
    let pitcherCategoriesAll = $("#pitcherTable thead th");
    // [position, type, 'IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'ER', 'ERA', 'WHIP', 'K9', 'QS', 'HLD', 'SV', 'SV_H', 'BSV', empty]

    //  Fielder, Pitcher的加總列
    let totalFielder = $("#fielderTable .total");
    let totalPitcher = $("#pitcherTable .total");

    // 每個欄位的加總值
    // 不包含AVG, OBP, SLG, OPS
    // 利用其他此Array的值去計算
    // 共18項
    let cateTotalFielder = [];

    // 不包含ERA, WHIP, K9
    // 利用其他此Array的值去計算
    // 共15項
    let cateTotalPitcher = [];
    // ['IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'K9', 'QS', 'HLD', 'SV', 'SV_H', 'BSV']

    // 先宣告之後要用來判斷目前是否有球員資料的Bool
    // 用來確認是否全部為-/-, -
    let hasValueFielder = false;
    let hasValuePitcher = false;

    /* 
    ================================
    設定BN列的CSS。

    因為HTML寫法的原因
    所以在載入後才指派tr元素的bench class
    ================================
    */
    function addBenchCSS() {
        positionButtons = $(".positionButton");
        positionButtons.each(function () {
            if ($(this).text() == "BN") {
                $(this).parent().parent().addClass("bench");
            }
        })
    }
    addBenchCSS();

    //  所有自己選的Fielder, Pitcher
    let fielders = $("#fielderTable tbody tr");
    let pitchers = $("#pitcherTable tbody tr");
    console.log(fielders);
    /*
    =================================
    處理剛載入網頁後
    Fielder, Pitcher表格中，Totals列的計算。

    會直接根據元素的內容去做計算。
    =================================
    */
    function calculateTotalAfterLoading() {
        // Fielder

        // 第一個-4: position, player, first, empty不用取
        // 第二個-4: AVG, OBP, SLG, OPS不用取，因為算法不是相加
        for (let i = 0; i < fielderCategoriesAll.length - 4 - 4; i++) {
            cateTotalFielder.push(0);
        }



        // 加總每個row
        fielders.each(function () {
            // 只要有一個不是-/-，Total就會有值
            if ($(this).children().eq(2).text() == "-/-") {
                return true;
            }
            else if ($(this).children().eq(1).text() == "Starting Lineup Totals") {
                return false;
            }
            for (let i = 0; i < cateTotalFielder.length; i++) {
                $(this).removeClass("editable");
                $(this).find(".positionButton").removeClass("positionButton");
                hasValueFielder = true;
                if (!$(this).hasClass("bench")) {
                    cateTotalFielder[i] += Number($(this).children().eq(i + 3).text());
                };
            }
        });


        // 映出total


        // 全部都是-/-，尚未有資料
        if (!hasValueFielder) {
            // position, name, empty不用設定
            for (let i = 0; i < fielderCategoriesAll.length - 3; i++) {
                if (i == 0) {
                    totalFielder.children().eq(i + 2).text("-/-");
                }
                totalFielder.children().eq(i + 2).text("-");
            }
        }
        // 有資料
        else {
            for (let i = 0; i < cateTotalFielder.length; i++) {
                if (i == 0) {
                    totalFielder.children().eq(i + 2).text(cateTotalFielder[4] + "/" + cateTotalFielder[1]);
                }
                else {
                    totalFielder.children().eq(i + 2).text(cateTotalFielder[i - 1]);
                }
            }
            // AVG, OBP, SLG, OPS另外設定
            for (let i = 0; i < 4; i++) {
                let value;
                switch (i) {
                    // AVG
                    case 0:
                        value = cateTotalFielder[4] / cateTotalFielder[1];
                        break;
                    // OBP
                    case 1:
                        value = (cateTotalFielder[4] + cateTotalFielder[10] + cateTotalFielder[11] + cateTotalFielder[12]) / (cateTotalFielder[1] + cateTotalFielder[10] + cateTotalFielder[11] + cateTotalFielder[12] + cateTotalFielder[14]);
                        break;
                    // SLG
                    case 2:
                        value = cateTotalFielder[8] / cateTotalFielder[1];
                        break;
                    // OPS
                    case 3:
                        value = (cateTotalFielder[4] + cateTotalFielder[10] + cateTotalFielder[11] + cateTotalFielder[12]) / (cateTotalFielder[1] + cateTotalFielder[10] + cateTotalFielder[11] + cateTotalFielder[12] + cateTotalFielder[14]) + cateTotalFielder[8] / cateTotalFielder[1];
                        break;
                }
                // 浮點數格式設定
                if (value >= 1) {
                    value = value.toFixed(3);
                }
                else {
                    value = value.toFixed(3).slice(1);
                }
                totalFielder.children().eq(i + 21).text(value);
            }
        }

        // Pitcher

        // -3: position, type, empty
        // -3: ERA, WHIP, K9
        for (let i = 0; i < pitcherCategoriesAll.length - 3 - 3; i++) {
            cateTotalPitcher.push(0);
        }

        pitchers.each(function () {
            if ($(this).children().eq(2).text() == "-") {
                return true;
            }
            else if ($(this).children().eq(1).text() == "Starting Lineup Totals") {
                return false;
            }
            for (let i = 0; i < cateTotalPitcher.length; i++) {
                $(this).removeClass("editable");
                $(this).find(".positionButton").removeClass("positionButton");
                hasValuePitcher = true;

                if (!$(this).hasClass("bench")) {
                    // IP要例外處理，因為有進位問題
                    if (i == 0) {
                        cateTotalPitcher[i] += Number($(this).children().eq(i + 2).text());
                        let int = parseInt(cateTotalPitcher[i]);
                        let decimal = parseFloat(cateTotalPitcher[i]) - int;
                        if (decimal * 10 / 3 >= 1) {
                            int++;
                            decimal -= 0.3;
                        }
                        cateTotalPitcher[i] = int + decimal;
                    }
                    // ERA, WHIP, K9之前的比項
                    else if (i < 10) {
                        cateTotalPitcher[i] += Number($(this).children().eq(i + 2).text());
                    }
                    // ERA, WHIP, K9之後的比項
                    else {
                        cateTotalPitcher[i] += Number($(this).children().eq(i + 5).text());
                    }
                }
            }
        });


        // 映出total

        // 全部都是-，尚未有資料
        if (!hasValuePitcher) {
            // position, type, empty略過
            for (let i = 0; i < pitcherCategoriesAll - 3; i++) {
                totalPitcher.children().eq(i + 2).text("-");
            }
        }
        else {
            for (let i = 0; i < cateTotalPitcher.length; i++) {
                if (i == 0) {
                    totalPitcher.children().eq(i + 2).text(cateTotalPitcher[i].toFixed(1));
                }
                else if (i < 10) {
                    totalPitcher.children().eq(i + 2).text(cateTotalPitcher[i]);
                }
                else {
                    totalPitcher.children().eq(i + 5).text(cateTotalPitcher[i]);
                }
            }
            let IP, int, decimal, IPDecimal;
            IP = cateTotalPitcher[0];
            int = parseInt(IP);
            decimal = parseFloat(IP) - int;
            IPDecimal = int + decimal * 10 * 3 ** -1;
            for (let i = 0; i < 3; i++) {
                let value;
                switch (i) {
                    // ERA : ER * 9 / IP
                    case 0:
                        // IP: 0.0 但有掉分
                        if (IPDecimal == 0 && cateTotalPitcher[9]) {
                            value = "INF";
                            totalPitcher.children().eq(i + 12).text(value);
                        }
                        else {
                            value = cateTotalPitcher[9] * 9 / IPDecimal;
                            totalPitcher.children().eq(i + 12).text(value.toFixed(2));
                        }
                        break;
                    // WHIP: H + BB / IP
                    case 1:
                        // IP: 0.0 但有人上壘
                        if (IPDecimal == 0 && (cateTotalPitcher[3] + cateTotalPitcher[5])) {
                            value = "INF";
                            totalPitcher.children().eq(i + 12).text(value);
                        }
                        else {
                            value = (cateTotalPitcher[3] + cateTotalPitcher[5]) / IPDecimal;
                            totalPitcher.children().eq(i + 12).text(value.toFixed(2));
                        }
                        break;
                    // K9: K * 9 / IP
                    case 2:
                        if (IPDecimal == 0) {
                            value = 0;
                        }
                        else {
                            value = (cateTotalPitcher[7] * 9) / IPDecimal;
                        }
                        totalPitcher.children().eq(i + 12).text(value.toFixed(2));
                        break;
                }

            }
        }
    }
    calculateTotalAfterLoading();


    function swapElement(type, e1, e2) {
        e1Position = e1.find(".positionButton").text();
        e2Position = e2.find(".positionButton").text();

        let temp = $("<tr></tr>").insertBefore(e1);
        e1.insertAfter(e2);
        e2.insertBefore(temp);
        temp.remove();

        e1.find(".positionButton").text(e2Position);
        e2.find(".positionButton").text(e1Position);

        if (type == "Fielder") {
            if (e1.index() >= 10) {
                e1.addClass("bench");
                e2.removeClass("bench");
            }
            else if (e2.index() >= 10) {
                e1.removeClass("bench");
                e2.addClass("bench");
            }
        }
        else if (type == "Pitcher") {
            if (e1.index() >= 6) {
                e1.addClass("bench");
                e2.removeClass("bench");
            }
            else if (e2.index() >= 6) {
                e1.removeClass("bench");
                e2.addClass("bench");
            }
        }

    }
    // 點擊某列球員後
    // 依據球員的守位以及所在格子，加入對應的CSS
    function handleEditableFielder() {
        let clickPlayer = $(this);

        // 在開始前，先清除所有前面存在的事件處理器
        // 目的是要防止連續的啟動此事件
        $("#fielderTable .editable").off("mouseenter mouseleave click");

        // 為點擊的球員，增加一個class
        clickPlayer.addClass("swapactive");

        console.log($("#message").attr("value"));
        // 宣告後面傳送AJAX請求時要傳送的資料
        let sendData = {
            "account": account,
            "type": "Fielder",
            "active": {},
            "target": {}
        };

        // 點擊的球員的守位，之後會對每個守位都進行判斷
        let activePosition = clickPlayer.find(".playerInfo").text().trim().split(" - ")[1].split(", ");

        // 判斷每個所選球員是否可以與點擊球員做交換
        $("#fielderTable .editable").each(function () {
            let row = $(this);
            // 略過自己
            if (clickPlayer.index() == row.index()) { return true; }

            // 判斷每個球員的每個守位
            let rowPosition = row.find(".playerInfo").text().trim().split(" - ")[1].split(", ");
            for (let i = 0; i < activePosition.length; i++) {
                for (let j = 0; j < rowPosition.length; j++) {
                    if ((row.find(".positionButton").text() == activePosition[i] ||
                        row.find(".positionButton").text() == "Util" ||
                        row.find(".positionButton").text() == "BN") &&
                        (clickPlayer.find(".positionButton").text() == rowPosition[j] ||
                            clickPlayer.find(".positionButton").text() == "Util" ||
                            clickPlayer.find(".positionButton").text() == "BN"
                        )) {
                        // 為符合的球員，新增一個class
                        row.addClass("swaptarget");
                    }
                }
            }
            // 加入最後一列的BN

            // 不符合條件的球員，會設定原本.editable:hover的CSS失效
            // 變成以jQuery的事件，取代使用:hover
            if (!row.hasClass("swapactive") && !row.hasClass("swaptarget")) {
                row.on("mouseenter", function () {
                    $(this).css("background", "white");
                });
            }

            // swaptarget的球員，在滑鼠移到該列時，會變的更綠
            else if (row.hasClass("swaptarget")) {
                row.on({
                    "mouseenter": function () {
                        $(this).css("background", "rgba(17, 113, 12, 0.4)");
                    },
                    "mouseleave": function () {
                        $(this).css("background", "rgba(93, 182, 88, 0.4)");
                    }
                })
            }

        })
        // 點擊自己本身
        $("#fielderTable .swapactive").on("click", function () {
            $("#fielderTable .swapactive").removeClass("swapactive");
            $("#fielderTable .swaptarget").removeClass("swaptarget");

            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#fielderTable .editable").off("click");
            $("#fielderTable .editable").removeAttr("style").off("mouseenter");
            $("#fielderTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditableFielder);

        });

        // 點擊可交換球員
        $("#fielderTable .swaptarget").on("click", function () {
            let target = $(this);


            sendData["active"]["ID"] = Number(clickPlayer.find("a").attr("href").slice(-4));
            sendData["active"]["index"] = clickPlayer.index();

            sendData["target"]["ID"] = Number(target.find("a").attr("href").slice(-4));
            sendData["target"]["index"] = target.index();

            // 這邊要實作交換球員列
            $.ajax({
                url: "/myteam/update",
                type: "POST",
                data: JSON.stringify(sendData),
                contentType: "application/json",
                dataType: "json",
                success: function (response) {
                    swapElement("Fielder", clickPlayer, target);
                }
            });


            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#fielderTable .swapactive").removeClass("swapactive");
            $("#fielderTable .swaptarget").removeClass("swaptarget");
            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#fielderTable .editable").off("click");
            $("#fielderTable .editable").removeAttr("style").off("mouseenter");
            $("#fielderTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditableFielder);
        });

        // 處理點擊後，經過判斷後無法與所點選球員做交換的球員
        $("#fielderTable .editable").not(".swapactive, .swaptarget").css({
            "opacity": "0.3",
            "cursor": "default"
        }).on("click", function () {
            $("#fielderTable .swapactive").removeClass("swapactive");
            $("#fielderTable .swaptarget").removeClass("swaptarget");

            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#fielderTable .editable").off("click");
            $("#fielderTable .editable").removeAttr("style").off("mouseenter");
            $("#fielderTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditableFielder);
        });

    }
    // 原神 啟動!
    $("#fielderTable .editable").on("click", handleEditableFielder);


    function handleEditablePitcher() {
        let clickPlayer = $(this);

        // 在開始前，先清除所有前面存在的事件處理器
        // 目的是要防止連續的啟動此事件
        $("#pitcherTable .editable").off("mouseenter mouseleave click");


        clickPlayer.addClass("swapactive");
        let sendData = {
            "account": account,
            "type": "Pitcher",
            "active": {},
            "target": {}
        };
        let activePosition = clickPlayer.find(".playerInfo").text().trim().split(" - ")[1].split(", ");
        $("#pitcherTable .editable").each(function () {
            let row = $(this);
            // 略過自己
            if (clickPlayer.index() == row.index()) { return true; }
            let rowPosition = row.find(".playerInfo").text().trim().split(" - ")[1].split(", ");
            for (let i = 0; i < activePosition.length; i++) {
                for (let j = 0; j < rowPosition.length; j++) {
                    if ((row.find(".positionButton").text() == activePosition[i] ||
                        row.find(".positionButton").text() == "BN") &&
                        (clickPlayer.find(".positionButton").text() == rowPosition[j] ||
                            clickPlayer.find(".positionButton").text() == "BN"
                        )) {
                        row.addClass("swaptarget");
                    }
                }
            }
            if (!row.hasClass("swapactive") && !row.hasClass("swaptarget")) {
                row.on("mouseenter", function () {
                    $(this).css("background", "white");
                });
            }
            else if (row.hasClass("swaptarget")) {
                row.on({
                    "mouseenter": function () {
                        $(this).css("background", "rgba(17, 113, 12, 0.4)");
                    },
                    "mouseleave": function () {
                        $(this).css("background", "rgba(93, 182, 88, 0.4)");
                    }
                })
            }

        })
        // 點擊自己本身
        $("#pitcherTable .swapactive").on("click", function () {
            $("#pitcherTable .swapactive").removeClass("swapactive");
            $("#pitcherTable .swaptarget").removeClass("swaptarget");

            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#pitcherTable .editable").off("click");
            $("#pitcherTable .editable").removeAttr("style").off("mouseenter");
            $("#pitcherTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditablePitcher);

        });

        // 點擊可交換球員
        $("#pitcherTable .swaptarget").on("click", function () {
            let target = $(this);

            sendData["active"]["ID"] = Number(clickPlayer.find("a").attr("href").slice(-4));
            sendData["active"]["index"] = clickPlayer.index();

            sendData["target"]["ID"] = Number(target.find("a").attr("href").slice(-4));
            sendData["target"]["index"] = target.index();

            // 這邊要實作交換球員列
            $.ajax({
                url: "/myteam/update",
                type: "POST",
                data: JSON.stringify(sendData),
                contentType: "application/json",
                dataType: "json",
                success: function (response) {
                    swapElement("Pitcher", clickPlayer, target);
                }
            });


            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#pitcherTable .swapactive").removeClass("swapactive");
            $("#pitcherTable .swaptarget").removeClass("swaptarget");
            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#pitcherTable .editable").off("click");
            $("#pitcherTable .editable").removeAttr("style").off("mouseenter");
            $("#pitcherTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditablePitcher);
        });

        // 處理點擊後，經過判斷後無法與所點選球員做交換的球員
        $("#pitcherTable .editable").not(".swapactive, .swaptarget").css({
            "opacity": "0.3",
            "cursor": "default"
        }).on("click", function () {
            $("#pitcherTable .swapactive").removeClass("swapactive");
            $("#pitcherTable .swaptarget").removeClass("swaptarget");

            // ** 在事件的最後，關閉所有此事件之內的事件，並重新綁定click事件
            $("#pitcherTable .editable").off("click");
            $("#pitcherTable .editable").removeAttr("style").off("mouseenter");
            $("#pitcherTable .editable").removeAttr("style").off("mouseleave").on("click", handleEditablePitcher);
        });

    }
    // 原神 啟動!
    $("#pitcherTable .editable").on("click", handleEditablePitcher);
})