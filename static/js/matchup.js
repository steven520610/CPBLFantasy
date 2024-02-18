$(document).ready(function () {
    // 計算AVG, OBP, SLG, OPS的function
    function calculateFielderStat(statName, valueArray) {
        let value;
        switch (statName) {
            case "AVG":
                value = valueArray[4] / valueArray[1];
                break;
            case "OBP":
                value = (valueArray[4] + valueArray[10] + valueArray[11] + valueArray[12]) / (valueArray[1] + valueArray[10] + valueArray[11] + valueArray[12] + valueArray[14]);
                break;
            case "SLG":
                value = valueArray[8] / valueArray[1];
                break;
            case "OPS":
                value = (valueArray[4] + valueArray[10] + valueArray[11] + valueArray[12]) / (valueArray[1] + valueArray[10] + valueArray[11] + valueArray[12] + valueArray[14]) + valueArray[8] / valueArray[1];
                break;
        }
        return value;
    }

    // 調整AVG, OBP, SLG, OPS顯示時的格式設定
    function adjustFielderStatFormat(index, value, element) {
        if (value >= 1) {
            element.children().eq(index).text(value.toFixed(3));
        }
        else if (isNaN(value)) {
            element.children().eq(index).text(".000");
        }
        else {
            element.children().eq(index).text(value.toFixed(3).slice(1));
        }
    }



    // 計算ERA, WHIP, K9的function
    // 加上type的原因是計算當日與當週成績時
    // 所傳入的valueArray長度不一樣
    // 至於為什麼Fielder不用是因為無論是當日還當週，前18個值都是一樣的。
    function calculatePitcherStat(type, statName, valueArray, IP) {
        let value;
        if (type == "Today") {
            switch (statName) {
                case "ERA":
                    if (IP == 0 && valueArray[9]) {
                        value = "INF";
                    }
                    else if (IP == 0 && !valueArray[9]) {
                        value = 0;
                    }
                    else {
                        value = valueArray[9] * 9 / IP;
                    }
                    break;
                case "WHIP":
                    if (IP == 0 && (valueArray[3] + valueArray[5])) {
                        value = "INF";
                    }
                    else if (IP == 0 && !(valueArray[3] + valueArray[5])) {
                        value = 0;
                    }
                    else {
                        value = (valueArray[3] + valueArray[5]) / IP;
                    }
                    break;
                case "K9":
                    if (IP == 0) {
                        value = 0;
                    }
                    else {
                        value = (valueArray[7] * 9) / IP;
                    }
                    break;
            }
        }
        else if (type == "Weekly") {
            switch (statName) {
                case "ERA":
                    if (IP == 0 && valueArray[27]) {
                        value = "INF";
                    }
                    else if (IP == 0 && !valueArray[27]) {
                        value = 0;
                    }
                    else {
                        value = valueArray[27] * 9 / IP;
                    }
                    break;
                case "WHIP":
                    if (IP == 0 && (valueArray[21] + valueArray[23])) {
                        value = "INF";
                    }
                    else if (IP == 0 && !(valueArray[21] + valueArray[23])) {
                        value = 0;
                    }
                    else {
                        value = (valueArray[21] + valueArray[23]) / IP;
                    }
                    break;
                case "K9":
                    if (IP == 0) {
                        value = 0;
                    }
                    else {
                        value = (valueArray[25] * 9) / IP;
                    }
                    break;
            }
        }
        return value;
    }

    // 調整AVG, OBP, SLG, OPS顯示時的格式設定
    function adjustPitcherStatFormat(index, value, element) {
        if (value == "INF") {
            element.children().eq(index).text(value);
        }
        else {
            element.children().eq(index).text(value.toFixed(2));
        }
    }

    /* 此function有兩種處理方式
    1. 把加總後的IP(小數 >= 0.3)轉換成合法的三進制IP
    2. 把三進制IP轉成十進制IP，以利ERA, WHIP, K9的計算 
    */
    function convertIP(IP, IPType) {
        // 轉成三進制
        if (IPType == "Trinary") {
            let int = parseInt(IP);
            let decimal = parseFloat(IP) - int;
            if (decimal * 10 / 3 >= 1) {
                int++;
                decimal -= 0.3;
            }
            return int + decimal;
        }

        // 轉成十進制
        else if (IPType == "Decimal") {
            let int = parseInt(IP);
            let decimal = parseFloat(IP) - int;
            return int + decimal * 10 * 3 ** -1;
        }
    }

    function compareWeekly() {
        const higherWorseIndex = [9, 13, 17, 24, 25, 26, 27, 28, 30, 31, 32, 33, 39];
        let myElement;
        let oppElement;
        // 加入AVG, OBP, SLG, OPS
        // 加入ERA, WHIP, K9
        // 去比
        for (let i = 0; i < cateTotalWeeklyStatsMy.length + 7; i++) {
            // IP不比
            if (i == 22) {
                continue;
            }
            myElement = myRow.children().eq(i + 2);
            oppElement = oppRow.children().eq(i + 2);

            myElement.removeClass("win");
            oppElement.removeClass("win");

            if (Number(myElement.text()) > Number(oppElement.text())) {
                if (higherWorseIndex.includes(i)) {
                    oppElement.addClass("win");
                }
                else {
                    myElement.addClass("win");
                }
            }
            else if (Number(myElement.text()) < Number(oppElement.text())) {
                if (higherWorseIndex.includes(i)) {
                    myElement.addClass("win");
                }
                else {
                    oppElement.addClass("win");
                }
            }
            // 平手就不需要處理
            // 因為一開始就已經remove win這個class了
        }
        let myWin = myRow.find(".stat.win").length;
        let oppWin = oppRow.find(".stat.win").length;

        myRow.find(".points").text(myWin);
        oppRow.find(".points").text(oppWin);

        myRow.find(".points").removeClass("totalWin");
        oppRow.find(".points").removeClass("totalWin");

        if (myWin > oppWin) {
            myRow.find(".points").addClass("totalWin");
        }
        else if (myWin < oppWin) {
            oppRow.find(".points").addClass("totalWin");
        }
    }
    // ------------------------------------以上為資料處理的function------------------------------------

    // ------------------------------------以下為全域變數------------------------------------
    const socket = io("http://127.0.0.1:5000/matchup");

    // default會執行的event
    socket.on("connect", function () {
        console.log("Connect!");
    });
    //  Fielder, Pitcher在db內的所有欄位
    //  但在後面宣告回圈時，直接手動指定欄位數量就好了
    //  所以這邊就只是方便查看用的

    // Fielder
    // let fielderCategoriesAll = $("#fielderTable thead th");
    // 24
    // [type, first, 'PA', 'AB', 'R', 'RBI', 'H', '2H', '3H', 'HR', 'TB', 'DP', 'BB', 'IBB', 'HBP', 'K', 'SF', 'BUNT', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS'
    // 1
    // ,position,
    // 24
    // type, first, 'PA', 'AB', 'R', 'RBI', 'H', '2H', '3H', 'HR', 'TB', 'DP', 'BB', 'IBB', 'HBP', 'K', 'SF', 'BUNT', 'SB', 'CS', 'AVG', 'OBP', 'SLG', 'OPS']

    // Pitcher
    // let pitcherCategoriesAll = $("#pitcherTable thead th");
    // 18
    // [type, 'IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'ER', 'ERA', 'WHIP', 'K9', 'QS', 'HLD', 'SV', 'SV_H', 'BSV'
    // 1
    // ,position,
    // 18
    // type, 'IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'ER', 'ERA', 'WHIP', 'K9', 'QS', 'HLD', 'SV', 'SV_H', 'BSV']

    //  所有自己選的Fielder, Pitcher
    let fielders = $("#fielderTable tbody tr");
    let pitchers = $("#pitcherTable tbody tr");
    //  Fielder, Pitcher的加總列
    let totalFielder = $("#fielderTable .total");
    let totalPitcher = $("#pitcherTable .total");

    // 自己、對手當週成績的列
    // 因為載入此網頁時，就會從server端那邊接收當週的成績了
    // 而如果當週目前都還沒有累計成績的話，也會有0這個數值
    // 所以不用把數值設成0
    // 也因為這個原因，只要處理有今日成績的狀況就好
    // 沒有的話可不做任何處理
    let h2hRows = $("#Head2Head tbody tr");
    let myRow = h2hRows.eq(0);
    let oppRow = h2hRows.eq(1);



    // 每個欄位的加總值
    // 不包含AVG, OBP, SLG, OPS
    // 利用其他此Array的值去計算
    // 共18項
    let cateTotalFielderMy = [];
    let cateTotalFielderOpp = [];
    // ['PA', 'AB', 'R', 'RBI', 'H', '2H', '3H', 'HR', 'TB', 'DP', 'BB', 'IBB', 'HBP', 'K', 'SF', 'BUNT', 'SB', 'CS']

    // 不包含ERA, WHIP, K9
    // 利用其他此Array的值去計算
    // 共15項
    let cateTotalPitcherMy = [];
    let cateTotalPitcherOpp = [];
    // ['IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'ER', 'QS', 'HLD', 'SV', 'SV_H', 'BSV']




    // 先宣告之後要用來判斷目前是否有球員資料的Bool
    // 用來確認是否全部為-/-, -
    let hasValueFielderMy = false
    let hasValueFielderOpp = false;

    let hasValuePitcherMy = false
    let hasValuePitcherOpp = false;




    // 儲存當週可以計算總和成績stats的陣列
    // 就是cateTotalFielder + cateTotalPitcher的內容
    // 共18 + 15項
    // ['PA', 'AB', 'R', 'RBI', 'H', '2H', '3H', 'HR', 'TB', 'DP', 'BB', 'IBB', 'HBP', 'K', 'SF', 'BUNT', 'SB', 'CS', 'IP', 'W', 'L', 'H', 'HR', 'BB', 'HBP', 'K', 'R', 'ER', 'QS', 'HLD', 'SV', 'SV_H', 'BSV']
    let cateTotalWeeklyStatsMy = [];
    let cateTotalWeeklyStatsOpp = [];


    // ------------------------------------以上為全域變數------------------------------------
    function addBench() {
        $(".bench").parent().addClass("bench");
    }
    addBench()

    // 一載入頁面就會先執行的function
    function Loading() {

        function calculateTotalLoading() {
            /*  處理剛載入網頁後
            Fielder, Pitcher表格中
            Totals列的計算
            因為從Flask載入HTML時已經傳入stats了
            所以就根據元素的內容去處理 */


            // Fielder
            // AVG, OBP, SLG, OPS這四個比項不用，因為算法不是相加
            for (let i = 0; i < 18; i++) {
                cateTotalFielderMy.push(0);
                cateTotalFielderOpp.push(0);
            }
            // 加總每個Fielder
            fielders.each(function () {
                // 因為自己與對手都在同一個row上
                // 所以要判斷兩個條件
                // 只要有一個不是-/-，Total就會有值
                if ($(this).children().eq(1).text() == "-/-" && $(this).children().eq(26).text() == "-/-") {
                    return true;
                }
                else if ($(this).children().eq(0).text() == "Totals") {
                    return false;
                }

                // BN格的不列入計算
                if (!$(this).hasClass("bench")) {
                    // 自己有資料，對手無資料
                    if ($(this).children().eq(1).text() != "-/-" && $(this).children().eq(26).text() == "-/-") {
                        for (let i = 0; i < cateTotalFielderMy.length; i++) {
                            hasValueFielderMy = true;
                            cateTotalFielderMy[i] += Number($(this).children().eq(i + 2).text());
                        }
                    }
                    // 自己無、對手有
                    else if ($(this).children().eq(1).text() == "-/-" && $(this).children().eq(26).text() != "-/-") {
                        for (let i = 0; i < cateTotalFielderOpp.length; i++) {
                            hasValueFielderOpp = true;
                            cateTotalFielderOpp[i] += Number($(this).children().eq(i + 27).text());
                        }
                    }
                    // 皆有
                    else {
                        for (let i = 0; i < cateTotalFielderMy.length; i++) {
                            hasValueFielderMy = true;
                            hasValueFielderOpp = true;
                            cateTotalFielderMy[i] += Number($(this).children().eq(i + 2).text());
                            cateTotalFielderOpp[i] += Number($(this).children().eq(i + 27).text());
                        }
                    }
                }
            });




            // Pitcher
            // ERA, WHIP, K9 這三個比項不用
            for (let i = 0; i < 15; i++) {
                cateTotalPitcherMy.push(0);
                cateTotalPitcherOpp.push(0);
            }
            // 加總每個Pitcher
            pitchers.each(function () {
                if ($(this).children().eq(1).text() == "-" && $(this).children().eq(21).text() == "-") {
                    return true;
                }
                else if ($(this).children().eq(1).text() == "Totals") {
                    return false;
                }
                if (!$(this).hasClass("bench")) {
                    if ($(this).children().eq(1).text() != "-" && $(this).children().eq(21).text() == "-") {
                        hasValuePitcherMy = true;
                        for (let i = 0; i < cateTotalPitcherMy.length; i++) {
                            // IP要例外處理，因為有進位問題
                            if (i == 0) {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 1).text());
                                cateTotalPitcherMy[i] = convertIP(cateTotalPitcherMy[i], "Trinary");
                            }
                            // ERA, WHIP, K9之前的比項
                            else if (i < 10) {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 1).text());
                            }
                            // ERA, WHIP, K9之後的比項
                            else {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 4).text());
                            }
                        }
                    }
                    else if ($(this).children().eq(1).text() == "-" && $(this).children().eq(21).text() != "-") {
                        hasValuePitcherOpp = true;
                        for (let i = 0; i < cateTotalPitcherOpp.length; i++) {
                            // IP要例外處理，因為有進位問題
                            if (i == 0) {
                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 21).text());
                                cateTotalPitcherOpp[i] = convertIP(cateTotalPitcherOpp[i], "Trinary");
                            }
                            // ERA, WHIP, K9之前的比項
                            else if (i < 10) {
                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 21).text());
                            }
                            // ERA, WHIP, K9之後的比項
                            else {
                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 24).text());
                            }
                        }
                    }
                    else {
                        for (let i = 0; i < cateTotalPitcherMy.length; i++) {
                            hasValuePitcherMy = true;
                            hasValuePitcherOpp = true
                            // IP要例外處理，因為有進位問題
                            if (i == 0) {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 1).text());
                                cateTotalPitcherMy[i] = convertIP(cateTotalPitcherMy[i], "Trinary");

                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 21).text());
                                cateTotalPitcherOpp[i] = convertIP(cateTotalPitcherOpp[i], "Trinary");
                            }
                            // ERA, WHIP, K9之前的比項
                            else if (i < 10) {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 1).text());
                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 21).text());
                            }
                            // ERA, WHIP, K9之後的比項
                            else {
                                cateTotalPitcherMy[i] += Number($(this).children().eq(i + 4).text());
                                cateTotalPitcherOpp[i] += Number($(this).children().eq(i + 24).text());
                            }
                        }
                    }
                }
            });
        }

        // 顯示自己、對手的
        // 野手、投手的Total列資料
        function displayTodayLoading(playerType, target) {
            if (playerType == "Fielder") {
                if (target == "my") {
                    // +1是因為要處理first
                    for (let i = 0; i < cateTotalFielderMy.length + 1; i++) {
                        // first
                        if (i == 0) {
                            totalFielder.children().eq(i + 1).text(cateTotalFielderMy[4] + "/" + cateTotalFielderMy[1]);
                        }
                        else {
                            totalFielder.children().eq(i + 1).text(cateTotalFielderMy[i - 1]);
                        }
                    }
                    // AVG, OBP, SLG, OPS另外設定
                    for (let i = 0; i < 4; i++) {
                        let value;
                        switch (i) {
                            case 0:
                                value = calculateFielderStat("AVG", cateTotalFielderMy);
                                break;
                            case 1:
                                value = calculateFielderStat("OBP", cateTotalFielderMy);
                                break;
                            case 2:
                                value = calculateFielderStat("SLG", cateTotalFielderMy);
                                break;
                            case 3:
                                value = calculateFielderStat("OPS", cateTotalFielderMy);
                                break;
                        }
                        adjustFielderStatFormat(i + 20, value, totalFielder);
                    }
                }
                else if (target == "opp") {
                    for (let i = 0; i < cateTotalFielderOpp.length + 1; i++) {
                        // first
                        if (i == 0) {
                            totalFielder.children().eq(i + 26).text(cateTotalFielderOpp[4] + "/" + cateTotalFielderOpp[1]);
                        }
                        else {
                            totalFielder.children().eq(i + 26).text(cateTotalFielderOpp[i - 1]);
                        }
                    }

                    // AVG, OBP, SLG, OPS另外設定
                    for (let i = 0; i < 4; i++) {
                        let value;
                        switch (i) {
                            // AVG
                            case 0:
                                value = calculateFielderStat("AVG", cateTotalFielderOpp);
                                break;
                            // OBP
                            case 1:
                                value = calculateFielderStat("OBP", cateTotalFielderOpp);
                                break;
                            // SLG
                            case 2:
                                value = calculateFielderStat("SLG", cateTotalFielderOpp);
                                break;
                            // OPS
                            case 3:
                                value = calculateFielderStat("OPS", cateTotalFielderOpp);
                                break;
                        }
                        adjustFielderStatFormat(i + 45, value, totalFielder);
                    }
                }
            }

            else if (playerType == "Pitcher") {
                if (target == "my") {
                    for (let i = 0; i < cateTotalPitcherMy.length; i++) {
                        if (i == 0) {
                            totalPitcher.children().eq(i + 1).text(cateTotalPitcherMy[i].toFixed(1));
                        }
                        else if (i < 10) {
                            totalPitcher.children().eq(i + 1).text(cateTotalPitcherMy[i]);
                        }
                        else {
                            totalPitcher.children().eq(i + 4).text(cateTotalPitcherMy[i]);
                        }
                    }
                    // ERA, WHIP, K9
                    let IPDecimal = convertIP(cateTotalPitcherMy[0], "Decimal");
                    for (let i = 0; i < 3; i++) {
                        let value;
                        switch (i) {
                            case 0:
                                value = calculatePitcherStat("Today", "ERA", cateTotalPitcherMy, IPDecimal);
                                break;
                            case 1:
                                value = calculatePitcherStat("Today", "WHIP", cateTotalPitcherMy, IPDecimal);
                                break;
                            case 2:
                                value = calculatePitcherStat("Today", "K9", cateTotalPitcherMy, IPDecimal);
                                break;
                        }
                        adjustPitcherStatFormat(i + 11, value, totalPitcher);
                    }
                }
                else if (target == "opp") {
                    for (let i = 0; i < cateTotalPitcherOpp.length; i++) {
                        if (i == 0) {
                            totalPitcher.children().eq(i + 21).text(cateTotalPitcherOpp[i].toFixed(1));
                        }
                        else if (i < 10) {
                            totalPitcher.children().eq(i + 21).text(cateTotalPitcherOpp[i]);
                        }
                        else {
                            totalPitcher.children().eq(i + 24).text(cateTotalPitcherOpp[i]);
                        }
                    }
                    IPDecimal = convertIP(cateTotalPitcherOpp[0], "Decimal");
                    for (let i = 0; i < 3; i++) {
                        let value;
                        switch (i) {
                            case 0:
                                value = calculatePitcherStat("Today", "ERA", cateTotalPitcherOpp, IPDecimal);
                                break;
                            case 1:
                                value = calculatePitcherStat("Today", "WHIP", cateTotalPitcherOpp, IPDecimal);
                                break;
                            case 2:
                                value = calculatePitcherStat("Today", "K9", cateTotalPitcherOpp, IPDecimal);
                                break;
                        }
                        adjustPitcherStatFormat(i + 31, value, totalPitcher);
                    }
                }
            }
        }


        calculateTotalLoading();

        // 映出今日Fielder成績的total
        // 自己、對手全部都是-/-，尚未有資料
        if (!hasValueFielderMy && !hasValueFielderOpp) {
            // type不需設定，只有所有stats + first要設定
            for (let i = 0; i < 23; i++) {
                if (i == 0) {
                    totalFielder.children().eq(i + 1).text("-/-");
                    totalFielder.children().eq(i + 26).text("-/-");
                }
                else {
                    totalFielder.children().eq(i + 1).text("-");
                    totalFielder.children().eq(i + 26).text("-");
                }
            }
        }
        // 自己有、對手無
        else if (hasValueFielderMy && !hasValueFielderOpp) {
            displayTodayLoading("Fielder", "my");
        }
        // 自己無、對手有
        else if (!hasValueFielderMy && hasValueFielderOpp) {
            displayTodayLoading("Fielder", "opp");
        }
        // 兩邊都有資料
        else {
            displayTodayLoading("Fielder", "my");
            displayTodayLoading("Fielder", "opp");
        }

        // 映出今日Pitcher今日成績的total
        // 自己、對手皆無
        if (!hasValuePitcherMy && !hasValuePitcherOpp) {
            for (let i = 0; i < 18; i++) {
                totalPitcher.children().eq(i + 1).text("-");
                totalPitcher.children().eq(i + 21).text("-");
            }
        }
        // 自己有、對手無
        else if (hasValuePitcherMy && !hasValuePitcherOpp) {
            displayTodayLoading("Pitcher", "my");
        }
        // 自己無、對手有
        else if (!hasValuePitcherMy && hasValuePitcherOpp) {
            displayTodayLoading("Pitcher", "opp");
        }
        // 皆有
        else {
            displayTodayLoading("Pitcher", "my");
            displayTodayLoading("Pitcher", "opp");
        }

        // --------以上處理完今日Totals的顯示-------------

        // --------以下處理Weekly成績的計算-------------

        function calculateWeeklyLoading() {
            // Fielder
            // AVG, OBP, SLG, OPS這四個比項不用，因為算法不是相加
            for (let i = 0; i < 18; i++) {
                cateTotalWeeklyStatsMy.push(0);
                cateTotalWeeklyStatsOpp.push(0);
            }

            // Pitcher
            // ERA, WHIP, K9 這三個比項不用
            for (let i = 0; i < 15; i++) {
                cateTotalWeeklyStatsMy.push(0);
                cateTotalWeeklyStatsOpp.push(0);
            }



            // 載入當週成績總和的資料(也就是經過Flask載入db資料後，直接在模板上的資料)
            // Fielder
            // AVG, OBP, SLG, OPS不納入，等待後面處理
            for (let i = 0; i < 18; i++) {
                cateTotalWeeklyStatsMy[i] = Number(myRow.children().eq(i + 2).text()) + cateTotalFielderMy[i];
                cateTotalWeeklyStatsOpp[i] = Number(oppRow.children().eq(i + 2).text()) + cateTotalFielderOpp[i];
            }

            // Pitcher 
            // ERA, WHIP, K9不納入
            for (let i = 0; i < 15; i++) {
                if (i == 0) {
                    cateTotalWeeklyStatsMy[i + 18] = convertIP(Number(myRow.children().eq(i + 24).text()) + cateTotalPitcherMy[i], "Trinary");
                    cateTotalWeeklyStatsOpp[i + 18] = convertIP(Number(oppRow.children().eq(i + 24).text()) + cateTotalPitcherOpp[i], "Trinary");
                }
                else if (i < 10) {
                    cateTotalWeeklyStatsMy[i + 18] = Number(myRow.children().eq(i + 24).text()) + cateTotalPitcherMy[i];
                    cateTotalWeeklyStatsOpp[i + 18] = Number(oppRow.children().eq(i + 24).text()) + cateTotalPitcherOpp[i];
                }
                else {
                    cateTotalWeeklyStatsMy[i + 18] = Number(myRow.children().eq(i + 27).text()) + cateTotalPitcherMy[i];
                    cateTotalWeeklyStatsOpp[i + 18] = Number(oppRow.children().eq(i + 27).text()) + cateTotalPitcherOpp[i];
                }
            }
        }
        function displayWeeklyLoading() {
            // 直接指定WeeklyStats的數量了
            // +1是因為要處理first
            for (let i = 0; i < 33 + 1; i++) {
                // first
                if (i == 0) {
                    myRow.children().eq(1).text(cateTotalWeeklyStatsMy[4] + "/" + cateTotalWeeklyStatsMy[1]);
                    oppRow.children().eq(1).text(cateTotalWeeklyStatsOpp[4] + "/" + cateTotalWeeklyStatsOpp[1]);
                }
                // AVG之前
                else if (i < 19) {
                    myRow.children().eq(i + 1).text(cateTotalWeeklyStatsMy[i - 1]);
                    oppRow.children().eq(i + 1).text(cateTotalWeeklyStatsOpp[i - 1]);
                }
                // IP
                else if (i == 19) {
                    myRow.children().eq(i + 5).text(cateTotalWeeklyStatsMy[i - 1].toFixed(1));
                    oppRow.children().eq(i + 5).text(cateTotalWeeklyStatsOpp[i - 1].toFixed(1));
                }
                // ERA之前
                else if (i < 29) {
                    myRow.children().eq(i + 5).text(cateTotalWeeklyStatsMy[i - 1]);
                    oppRow.children().eq(i + 5).text(cateTotalWeeklyStatsOpp[i - 1]);
                }
                // K9之後
                else {
                    myRow.children().eq(i + 8).text(cateTotalWeeklyStatsMy[i - 1]);
                    oppRow.children().eq(i + 8).text(cateTotalWeeklyStatsOpp[i - 1]);
                }
            }
            // 處理AVG, OBP, SLG, OPS
            for (let i = 0; i < 4; i++) {
                let myValue;
                let oppValue;
                switch (i) {
                    case 0:
                        myValue = calculateFielderStat("AVG", cateTotalWeeklyStatsMy);
                        oppValue = calculateFielderStat("AVG", cateTotalWeeklyStatsOpp);
                        break;
                    case 1:
                        myValue = calculateFielderStat("OBP", cateTotalWeeklyStatsMy);
                        oppValue = calculateFielderStat("OBP", cateTotalWeeklyStatsOpp);
                        break;
                    case 2:
                        myValue = calculateFielderStat("SLG", cateTotalWeeklyStatsMy);
                        oppValue = calculateFielderStat("SLG", cateTotalWeeklyStatsOpp);
                        break;
                    case 3:
                        myValue = calculateFielderStat("OPS", cateTotalWeeklyStatsMy);
                        oppValue = calculateFielderStat("OPS", cateTotalWeeklyStatsOpp);
                        break;
                }
                adjustFielderStatFormat(i + 20, myValue, myRow);
                adjustFielderStatFormat(i + 20, oppValue, oppRow);
            }

            // ERA, WHIP, K9
            let IPDecimalMy = convertIP(cateTotalWeeklyStatsMy[18], "Decimal");
            let IPDecimalOpp = convertIP(cateTotalWeeklyStatsOpp[18], "Decimal");
            for (let i = 0; i < 3; i++) {
                let myValue;
                let oppValue;
                switch (i) {
                    case 0:
                        myValue = calculatePitcherStat("Weekly", "ERA", cateTotalWeeklyStatsMy, IPDecimalMy);
                        oppValue = calculatePitcherStat("Weekly", "ERA", cateTotalWeeklyStatsOpp, IPDecimalOpp);
                        break;
                    case 1:
                        myValue = calculatePitcherStat("Weekly", "WHIP", cateTotalWeeklyStatsMy, IPDecimalMy);
                        oppValue = calculatePitcherStat("Weekly", "WHIP", cateTotalWeeklyStatsOpp, IPDecimalOpp);
                        break;
                    case 2:
                        myValue = calculatePitcherStat("Weekly", "K9", cateTotalWeeklyStatsMy, IPDecimalMy);
                        oppValue = calculatePitcherStat("Weekly", "K9", cateTotalWeeklyStatsOpp, IPDecimalOpp);
                        break;
                }
                adjustPitcherStatFormat(i + 34, myValue, myRow);
                adjustPitcherStatFormat(i + 34, oppValue, oppRow);
            }
        }
        calculateWeeklyLoading();
        displayWeeklyLoading();
        compareWeekly();
    }

    // 一載入頁面就會先執行的function
    // 因此目前為止，載入頁面會執行：
    // 1. 計算自己、對手當日成績的Total
    // 2. 將今日成績加上當週成績並計算然後顯示
    // 3. 計算完之後比較當週成績
    Loading();

    function updateSingle(playerType, current, i, element, valueArray, weeklyArray) {
        if (playerType == "Fielder") {
            // 原本為 - 的情況
            if (current.text() == "-" || current.text() == "-/-") {
                if (i == 0) {
                    current.text("0/0");
                }
                // AVG, OBP, SLB, OPS
                else if (i >= 19) {
                    current.text(".000");
                }
                else {
                    current.text("0");
                }
                current.addClass("positive");
            }

            // 有data
            else {
                // H/AB
                if (i == 0) {
                    let oldH = Number(current.text().split("/")[0]);
                    let oldAB = Number(current.text().split("/")[1]);

                    let newH = element[7];
                    let newAB = element[4];

                    current.text(newH + "/" + newAB);

                    if (newH - oldH > 0) {
                        current.addClass("positive");
                    }
                    else if (newAB - oldAB > 0) {
                        current.addClass("negative");
                    }
                }
                // 剩餘項目顯示
                else {
                    let oldCate = Number(current.text());
                    let newCate = element[i + 2];
                    // AVG, OBP, SLG, OPS
                    if (i >= 19) {
                        if (newCate >= 1) {
                            newCate = newCate.toFixed(3);
                        }
                        else {
                            newCate = newCate.toFixed(3).slice(1);
                        }
                    }
                    current.text(newCate);

                    let difference = newCate - oldCate;
                    // 判斷數據變好or變壞
                    if (difference > 0) {
                        // DP, K, CS
                        if (i == 10 || i == 14 || i == 18) {
                            current.addClass("negative");
                        }
                        else {
                            current.addClass("positive");
                        }
                    }
                    else if (difference < 0) {
                        current.addClass("negative");
                    }

                    // 最後加總Total
                    // AVG, OBP, SLG, OPS不能直接加
                    // 0不會執行這邊，共有18個
                    if (i < 19) {
                        if (difference != 0) {
                            if (!current.parent().hasClass("bench")) {
                                valueArray[i - 1] += difference;
                                weeklyArray[i - 1] += difference
                            }
                        }
                    }
                }
            }
        }
        else if (playerType == "Pitcher") {
            // 原本為 -
            if (current.text() == "-") {
                if (i == 0) {
                    current.text("0.0");
                }
                else if (i >= 10 && i <= 12) {
                    current.text("0.00");
                }
                else {
                    current.text("0");
                }
                current.addClass("positive");
            }
            // 有資料
            else {
                let oldCate = Number(current.text());
                // 會根據比項，讓這兩個變數算法不一樣，所以到條件內再賦值
                let newCate, difference;

                // IP
                if (i == 0) {

                    newCate = element[i + 3];
                    difference = newCate - oldCate;

                    if (difference * 10 % 10 >= 8) {
                        difference -= 0.7;
                    }
                    // 加總IP Total
                    let int = parseInt(difference);
                    let decimal = parseFloat(difference) - int;

                    if (!current.parent().hasClass("bench")) {
                        valueArray[i] += int + decimal;
                        valueArray[i] = convertIP(valueArray[i], "Trinary");
                        weeklyArray[i + 18] += int + decimal;
                        weeklyArray[i + 18] = convertIP(weeklyArray[i + 18], "Trinary");
                    }
                    // 特效在此處處理
                    if (difference > 0) {
                        current.addClass("positive");
                    }
                    // IP的網頁文字
                    newCate = newCate.toFixed(1);
                }
                // ERA, WHIP, K9之前的項目
                else if (i < 10) {
                    newCate = element[i + 3];
                    difference = newCate - oldCate;

                    if (!current.parent().hasClass("bench")) {
                        valueArray[i] += difference;
                        weeklyArray[i + 18] += difference;
                    }
                    // 特效
                    if (difference > 0) {
                        // W, K, QS, HLD, SV, SV_H
                        if (i == 1 || i == 7) {
                            current.addClass("positive");
                        }
                        else {
                            current.addClass("negative");
                        }
                    }
                    else if (difference < 0) {
                        // H, HR, HBP, R, ER, QS
                        // 除了QS有可能隨時變動
                        // 其餘是為了防止紀錄的更動(ex:原本安打改失誤)
                        if (i == 3 || i == 4 || i == 6 || i == 8 || i == 9 || i == 13) {
                            current.addClass("positive");
                        }
                        else {
                            current.addClass("negative");
                        }
                    }
                }
                // ERA, WHIP, K9
                // 不做加總
                else if (i < 13) {

                    if (element[i + 3] > 1000) {
                        newCate = "INF";
                        if (!current.hasClass("negative")) {
                            current.addClass("negative");
                        }
                    }

                    else {
                        // 四捨五入到小數第二位
                        newCate = Math.round(element[i + 3] * 100) / 100;
                        if (oldCate == "INF") {
                            current.addClass("positive");
                        }
                        else {
                            difference = newCate - oldCate;
                            // 特效
                            // ERA, WHIP
                            if (i < 12) {
                                if (difference > 0) {
                                    current.addClass("negative");
                                }
                                else if (difference < 0) {
                                    current.addClass("positive");
                                }
                            }
                            // K9
                            else {
                                if (difference > 0) {
                                    current.addClass("positive");
                                }
                                else if (difference < 0) {
                                    current.addClass("negative");
                                }
                            }
                        }
                        // ERA, WHIP, K9的網頁文字
                        newCate = newCate.toFixed(2);
                    }

                }

                // 剩餘項目
                else {

                    newCate = element[i + 3];
                    difference = newCate - oldCate;

                    if (!current.parent().hasClass("bench")) {
                        valueArray[i - 3] += difference;
                        weeklyArray[i + 15] += difference;
                    }
                    // 特效
                    if (difference > 0) {
                        // QS, HLD, SV, SV_H
                        if (i == 17) {
                            current.addClass("negative");
                        }
                        else {
                            current.addClass("positive");
                        }
                    }
                    else if (difference < 0) {
                        // 因為除了QS有可能隨時變動
                        if (i == 13) {
                            current.addClass("negative");
                        }
                        else {
                            current.addClass("positive");
                        }
                    }
                }

                // 無論比項皆設定網頁文字
                current.text(newCate);
            }
        }
    }
    function updateTotal(type, playerType, target, valueArray, valueArrayOld) {
        if (type == "Today") {
            if (playerType == "Fielder") {
                // 多了一個first
                for (let i = 0; i < valueArray.length + 1; i++) {
                    // H/AB
                    if (i == 0) {
                        if (valueArray[4] - valueArrayOld[4] > 0) {
                            if (target == "my") {
                                totalFielder.children().eq(i + 1).addClass("positive");
                            }
                            else {
                                totalFielder.children().eq(i + 26).addClass("positive");
                            }
                        }
                        else if (valueArray[1] - valueArrayOld[1] > 0) {
                            if (target == "my") {
                                totalFielder.children().eq(i + 1).addClass("negative");
                            }
                            else {
                                totalFielder.children().eq(i + 26).addClass("negative");
                            }
                        }
                        if (target == "my") {
                            totalFielder.children().eq(i + 1).text(valueArray[4] + "/" + valueArray[1])
                        }
                        else {
                            totalFielder.children().eq(i + 26).text(valueArray[4] + "/" + valueArray[1])
                        }
                    }
                    // DP, K, CS
                    else if (i == 10 || i == 14 || i == 18) {
                        if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                            if (target == "my") {
                                totalFielder.children().eq(i + 1).addClass("negative");
                            }
                            else {
                                totalFielder.children().eq(i + 26).addClass("negative");
                            }
                        }
                    }
                    else {
                        if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                            if (target == "my") {
                                totalFielder.children().eq(i + 1).addClass("positive");
                            }
                            else {
                                totalFielder.children().eq(i + 26).addClass("positive");
                            }
                        }
                    }
                    // 設定total 比項資料
                    if (target == "my") {
                        totalFielder.children().eq(i + 1).text(valueArray[i - 1]);
                    }
                    else {
                        totalFielder.children().eq(i + 26).text(valueArray[i - 1]);
                    }
                }

                // AVG, OBP, SLG, OPS
                for (let i = 0; i < 4; i++) {
                    let oldValue;
                    let newValue;
                    if (valueArrayOld[0] == 0) {
                        oldValue = 0;
                    }
                    if (valueArray[0] == 0) {
                        newValue = 0;
                    }
                    else {
                        switch (i) {
                            case 0:
                                oldValue = calculateFielderStat("AVG", valueArrayOld);
                                newValue = calculateFielderStat("AVG", valueArray);
                                break;
                            case 1:
                                oldValue = calculateFielderStat("OBP", valueArrayOld);
                                newValue = calculateFielderStat("OBP", valueArray);
                                break;
                            case 2:
                                oldValue = calculateFielderStat("SLG", valueArrayOld);
                                newValue = calculateFielderStat("SLG", valueArray);
                                break;
                            case 3:
                                oldValue = calculateFielderStat("OPS", valueArrayOld);
                                newValue = calculateFielderStat("OPS", valueArray);
                                break;
                        }
                    }

                    // 加上特效的class
                    if (newValue - oldValue > 0) {
                        if (target == "my") {
                            totalFielder.children().eq(i + 20).addClass("positive");
                        }
                        else {
                            totalFielder.children().eq(i + 45).addClass("positive");
                        }
                    }
                    else if (newValue - oldValue < 0) {
                        if (target == "my") {
                            totalFielder.children().eq(i + 20).addClass("negative");
                        }
                        else {
                            totalFielder.children().eq(i + 45).addClass("negative");
                        }
                    }

                    if (newValue >= 1) {
                        if (target == "my") {
                            totalFielder.children().eq(i + 20).text(newValue.toFixed(3));
                        }
                        else {
                            totalFielder.children().eq(i + 45).text(newValue.toFixed(3));
                        }
                    }
                    else {
                        if (target == "my") {
                            totalFielder.children().eq(i + 20).text(newValue.toFixed(3).slice(1));
                        }
                        else {
                            totalFielder.children().eq(i + 45).text(newValue.toFixed(3).slice(1));
                        }
                    }
                }
            }
            else if (playerType == "Pitcher") {
                // 略過了ERA, WHIP, K9
                // 後面用另外一個回圈設定
                for (let i = 0; i < valueArray.length; i++) {
                    // IP
                    if (i == 0) {
                        if (valueArray[0] - valueArrayOld[0] > 0) {
                            if (target == "my") {
                                totalPitcher.children().eq(1).addClass("positive");
                            }
                            else {
                                totalPitcher.children().eq(21).addClass("positive");
                            }
                        }
                        // 設定total 比項資料
                        if (target == "my") {
                            totalPitcher.children().eq(1).text(valueArray[0].toFixed(1));
                        }
                        else {
                            totalPitcher.children().eq(21).text(valueArray[0].toFixed(1));
                        }
                    }

                    // 在ERA, WHIP, K9前的比項
                    else if (i < 10) {
                        // W, K
                        if (i == 1 || i == 7) {
                            if (valueArray[i] - valueArrayOld[i] > 0) {
                                if (target == "my") {
                                    totalPitcher.children().eq(i + 1).addClass("positive");
                                }
                                else {
                                    totalPitcher.children().eq(i + 21).addClass("positive");
                                }
                            }
                        }
                        else {
                            if (valueArray[i] - valueArrayOld[i] > 0) {
                                if (target == "my") {
                                    totalPitcher.children().eq(i + 1).addClass("negative");
                                }
                                else {
                                    totalPitcher.children().eq(i + 21).addClass("negative");
                                }
                            }
                        }
                        // 設定total 比項資料
                        if (target == "my") {
                            totalPitcher.children().eq(i + 1).text(valueArray[i]);
                        }
                        else {
                            totalPitcher.children().eq(i + 21).text(valueArray[i]);
                        }
                    }

                    // 在ERA, WHIP, K9後的比項
                    else {
                        // BSV
                        if (i == 14) {
                            if (valueArray[i] - valueArrayOld[i] > 0) {
                                if (target == "my") {
                                    totalPitcher.children().eq(i + 4).addClass("negative");
                                }
                                else {
                                    totalPitcher.children().eq(i + 24).addClass("negative");
                                }
                            }
                        }
                        else {
                            if (valueArray[i] - valueArrayOld[i] > 0) {
                                if (target == "my") {
                                    totalPitcher.children().eq(i + 4).addClass("positive");
                                }
                                else {
                                    totalPitcher.children().eq(i + 24).addClass("positive");
                                }
                            }
                            else if (valueArray[i] - valueArrayOld[i] < 0) {
                                if (target == "my") {
                                    totalPitcher.children().eq(i + 4).addClass("negative");
                                }
                                else {
                                    totalPitcher.children().eq(i + 24).addClass("negative");
                                }
                            }
                        }
                        // 設定total 比項資料
                        if (target == "my") {
                            totalPitcher.children().eq(i + 4).text(valueArray[i]);
                        }
                        else {
                            totalPitcher.children().eq(i + 24).text(valueArray[i]);
                        }
                    }
                }
                let oldIPDecimal = convertIP(valueArrayOld[0], "Decimal");
                let newIPDecimal = convertIP(valueArray[0], "Decimal");

                // ERA, WHIP, K9
                for (let i = 0; i < 3; i++) {
                    let oldValue;
                    let newValue;
                    switch (i) {
                        case 0:
                            oldValue = calculatePitcherStat(type, "ERA", valueArrayOld, oldIPDecimal);
                            if (oldValue == "INF") { oldValue = 0 };

                            newValue = calculatePitcherStat(type, "ERA", valueArray, newIPDecimal);
                            if (newValue == "INF") { newValue = 0 };

                            // IP: 0, ER > 0
                            if (target == "my") {
                                if (newValue == 0 && valueArray[9] > 0) {
                                    totalPitcher.children().eq(i + 11).text("INF");
                                    if (totalPitcher.children().eq(i + 11).text() != "INF") {
                                        totalPitcher.children().eq(i + 11).addClass("negative");
                                    }
                                }
                                else {
                                    totalPitcher.children().eq(i + 11).text(newValue.toFixed(2));
                                }
                            }
                            else {
                                if (newValue == 0 && valueArray[9] > 0) {
                                    totalPitcher.children().eq(i + 31).text("INF");
                                    if (totalPitcher.children().eq(i + 31).text() != "INF") {
                                        totalPitcher.children().eq(i + 31).addClass("negative");
                                    }
                                }
                                else {
                                    totalPitcher.children().eq(i + 31).text(newValue.toFixed(2));
                                }
                            }
                            break;
                        case 1:
                            oldValue = calculatePitcherStat(type, "WHIP", valueArrayOld, oldIPDecimal);
                            newValue = calculatePitcherStat(type, "WHIP", valueArray, newIPDecimal);
                            if (oldValue == "INF") { oldValue = 0 };
                            if (newValue == "INF") { newValue = 0 };

                            // IP: 0, H+BB > 0
                            if (target == "my") {
                                if (newValue == 0 && (valueArray[3] + valueArray[5]) > 0) {
                                    totalPitcher.children().eq(i + 11).text("INF");
                                    if (totalPitcher.children().eq(i + 11).text() != "INF") {
                                        totalPitcher.children().eq(i + 11).addClass("negative");
                                    }
                                }
                                else {
                                    totalPitcher.children().eq(i + 11).text(newValue.toFixed(2));
                                }
                            }
                            else {
                                if (newValue == 0 && (valueArray[3] + valueArray[5]) > 0) {
                                    totalPitcher.children().eq(i + 31).text("INF");
                                    if (totalPitcher.children().eq(i + 31).text() != "INF") {
                                        totalPitcher.children().eq(i + 31).addClass("negative");
                                    }
                                }
                                else {
                                    totalPitcher.children().eq(i + 31).text(newValue.toFixed(2));
                                }
                            }
                            break;
                        case 2:
                            oldValue = calculatePitcherStat(type, "K9", valueArrayOld, oldIPDecimal);
                            newValue = calculatePitcherStat(type, "K9", valueArray, newIPDecimal);
                            if (target == "my") {
                                totalPitcher.children().eq(i + 11).text(newValue.toFixed(2));
                            }
                            else {
                                totalPitcher.children().eq(i + 31).text(newValue.toFixed(2));
                            }
                            break;
                    }


                    if (newValue - oldValue > 0) {
                        if (i < 2) {
                            if (target == "my") {
                                totalPitcher.children().eq(i + 11).addClass("negative");
                            }
                            else {
                                totalPitcher.children().eq(i + 31).addClass("negative");
                            }
                        }
                        else {
                            if (target == "my") {
                                totalPitcher.children().eq(i + 11).addClass("positive");
                            }
                            else {
                                totalPitcher.children().eq(i + 31).addClass("positive");
                            }
                        }
                    }
                    else if (newValue - oldValue < 0) {
                        if (i < 2) {
                            if (target == "my") {
                                totalPitcher.children().eq(i + 11).addClass("positive");
                            }
                            else {
                                totalPitcher.children().eq(i + 31).addClass("positive");
                            }
                        }
                        else {
                            if (target == "my") {
                                totalPitcher.children().eq(i + 11).addClass("negative");
                            }
                            else {
                                totalPitcher.children().eq(i + 31).addClass("negative");
                            }
                        }
                    }
                }
            }
        }
        else if (type == "Weekly") {
            // 不需要再分playerType了，因為Weekly是存在同一個Array內
            if (target == "my") { element = myRow; }
            else if (target == "opp") { element = oppRow; }


            // 設定valueArray中的比項的特效
            // 多了一個first要處理
            for (let i = 0; i < valueArray.length + 1; i++) {
                // first
                if (i == 0) {
                    if (valueArray[4] - valueArrayOld[4] > 0) {
                        element.children().eq(i + 1).addClass("positive");
                    }
                    else if (valueArray[1] - valueArrayOld[1] > 0) {
                        element.children().eq(i + 1).addClass("negative");
                    }
                    element.children().eq(i + 1).text(valueArray[4] + "/" + valueArray[1]);
                }
                // DP, K, CS
                else if (i == 10 || i == 14 || i == 18) {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 1).addClass("negative");
                    }
                }
                // Fielder剩餘比項
                else if (i < 19) {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 1).addClass("positive");
                    }
                }
                // W, K
                else if (i == 20 || i == 26) {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 5).addClass("positive");
                    }
                }
                // ERA前剩餘Pitcher比項
                else if (i < 29) {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 5).addClass("negative");
                    }
                }
                // ERA, WHIP, K9後
                // BSV
                else if (i == 33) {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 8).addClass("negative");
                    }
                }
                // 剩餘
                else {
                    if (valueArray[i - 1] - valueArrayOld[i - 1] > 0) {
                        element.children().eq(i + 8).addClass("positive");
                    }

                }
            }
            // 設定valueArray中的比項的資料
            // first前面特效時就設定過了，這邊就略過
            for (let i = 0; i < valueArray.length; i++) {
                // AVG前
                if (i < 18) {
                    element.children().eq(i + 2).text(valueArray[i]);
                }
                // IP
                else if (i == 18) {
                    element.children().eq(i + 6).text(valueArray[i].toFixed(1));
                }
                // ERA前
                else if (i < 28) {
                    element.children().eq(i + 6).text(valueArray[i]);
                }
                // K9後
                else {
                    element.children().eq(i + 9).text(valueArray[i]);
                }
            }

            // 設定非valueArray中的比項的資料
            // Fielder: AVG, OBP, SLG, OPS
            // Pitcher: ERA, WHIP, K9
            // AVG, OBP, SLG, OPS
            for (let i = 0; i < 4; i++) {
                let oldValue;
                let newValue;
                if (valueArrayOld[0] == 0) {
                    oldValue = 0;
                }
                if (valueArray[0] == 0) {
                    newValue = 0;
                }
                else {
                    switch (i) {
                        case 0:
                            oldValue = calculateFielderStat("AVG", valueArrayOld);
                            newValue = calculateFielderStat("AVG", valueArray);
                            break;
                        case 1:
                            oldValue = calculateFielderStat("OBP", valueArrayOld);
                            newValue = calculateFielderStat("OBP", valueArray);
                            break;
                        case 2:
                            oldValue = calculateFielderStat("SLG", valueArrayOld);
                            newValue = calculateFielderStat("SLG", valueArray);
                            break;
                        case 3:
                            oldValue = calculateFielderStat("OPS", valueArrayOld);
                            newValue = calculateFielderStat("OPS", valueArray);
                            break;
                    }
                }

                // 加上特效的class
                if (newValue - oldValue > 0) {
                    element.children().eq(i + 20).addClass("positive");
                }
                else if (newValue - oldValue < 0) {
                    element.children().eq(i + 20).addClass("negative");
                }

                if (newValue >= 1) {
                    element.children().eq(i + 20).text(newValue.toFixed(3));
                }
                else {
                    element.children().eq(i + 20).text(newValue.toFixed(3).slice(1));
                }
            }
            let oldIPDecimal = convertIP(valueArrayOld[18], "Decimal");
            let newIPDecimal = convertIP(valueArray[18], "Decimal");

            // ERA, WHIP, K9
            for (let i = 0; i < 3; i++) {
                let oldValue;
                let newValue;
                switch (i) {
                    case 0:
                        oldValue = calculatePitcherStat(type, "ERA", valueArrayOld, oldIPDecimal);
                        if (oldValue == "INF") { oldValue = 0 };

                        newValue = calculatePitcherStat(type, "ERA", valueArray, newIPDecimal);
                        if (newValue == "INF") { newValue = 0 };

                        // IP: 0, ER > 0
                        if (newValue == 0 && valueArray[27] > 0) {
                            element.children().eq(i + 34).text("INF");
                            if (element.children().eq(i + 34).text() != "INF") {
                                element.children().eq(i + 34).addClass("negative");
                            }
                        }
                        else {
                            element.children().eq(i + 34).text(newValue.toFixed(2));
                        }
                        break;
                    case 1:
                        oldValue = calculatePitcherStat(type, "WHIP", valueArrayOld, oldIPDecimal);
                        newValue = calculatePitcherStat(type, "WHIP", valueArray, newIPDecimal);
                        if (oldValue == "INF") { oldValue = 0 };
                        if (newValue == "INF") { newValue = 0 };

                        // IP: 0, H+BB > 0
                        if (newValue == 0 && (valueArray[21] + valueArray[23]) > 0) {
                            element.children().eq(i + 34).text("INF");
                            if (element.children().eq(i + 34).text() != "INF") {
                                element.children().eq(i + 34).addClass("negative");
                            }
                        }
                        else {
                            element.children().eq(i + 34).text(newValue.toFixed(2));
                        }
                        break;
                    case 2:
                        oldValue = calculatePitcherStat(type, "K9", valueArrayOld, oldIPDecimal);
                        newValue = calculatePitcherStat(type, "K9", valueArray, newIPDecimal);

                        element.children().eq(i + 34).text(newValue.toFixed(2));

                        break;
                }


                if (newValue - oldValue > 0) {
                    if (i < 2) {
                        element.children().eq(i + 34).addClass("negative");
                    }
                    else {
                        element.children().eq(i + 34).addClass("positive");
                    }
                }
                else if (newValue - oldValue < 0) {
                    if (i < 2) {
                        element.children().eq(i + 34).addClass("positive");
                    }
                    else {
                        element.children().eq(i + 34).addClass("negative");
                    }
                }
            }
        }
    }
    socket.on("update", function (response) {
        // deepcopy
        let cateTotalFielderOldMy = [...cateTotalFielderMy];
        let cateTotalFielderOldOpp = [...cateTotalFielderOpp];
        let cateTotalPitcherOldMy = [...cateTotalPitcherMy];
        let cateTotalPitcherOldOpp = [...cateTotalPitcherOpp];
        let cateTotalWeeklyStatsOldMy = [...cateTotalWeeklyStatsMy];
        let cateTotalWeeklyStatsOldOpp = [...cateTotalWeeklyStatsOpp];

        // Fielder
        let dbFielders = response["Fielder"];
        fielders.each(function () {
            let row = $(this);
            let rowPlayers = row.find(".player");
            let myPlayer = rowPlayers.eq(0).find("a");
            let oppPlayer = rowPlayers.eq(1).find("a");
            // 2:兩邊都有, 1:只有一邊有，但是需再分辨是哪一邊有球員, 0:兩邊都沒
            dbFielders.forEach(element => {
                // 每個tr會有兩個球員，自己、對手
                // 但db內的每筆資料一定只有一個球員會被選到
                // 因此要用條件區分是選到自己的球員 or 對手的球員

                // 根據名字來搜尋(用id可能更好)
                // 選到自己的球員
                if (myPlayer.text() == element[2] && row.find(".position").text() != "BN") {
                    hasValueFielderMy = true;
                    for (let i = 0; i < 23; i++) {

                        let current = $(this).children().eq(i + 1);
                        updateSingle("Fielder", current, i, element, cateTotalFielderMy, cateTotalWeeklyStatsMy);
                    }
                }
                // 選到的是對手的球員
                else if (oppPlayer.text() == element[2] && row.find(".position").text() != "BN") {
                    hasValueFielderOpp = true;
                    for (let i = 0; i < 23; i++) {

                        let current = $(this).children().eq(i + 26);
                        updateSingle("Fielder", current, i, element, cateTotalFielderOpp, cateTotalWeeklyStatsOpp);
                    }
                }
            });
        });

        // 每個球員加總完後，才觀察Total的差異
        // 分成四種case
        // 兩邊皆無
        // 自己有、對手無
        // 自己無、對手有
        // 兩邊都有
        if (!hasValueFielderMy && !hasValueFielderOpp) {
            for (let i = 0; i < 23; i++) {
                if (i == 0) {
                    totalFielder.children().eq(i + 1).text("-/-");
                    totalFielder.children().eq(i + 26).text("-/-");
                }
                else {
                    totalFielder.children().eq(i + 1).text("-");
                    totalFielder.children().eq(i + 26).text("-");
                }
            }
        }
        else if (hasValueFielderMy && !hasValueFielderOpp) {
            updateTotal("Today", "Fielder", "my", cateTotalFielderMy, cateTotalFielderOldMy);
        }
        else if (!hasValueFielderMy && hasValueFielderOpp) {
            updateTotal("Today", "Fielder", "opp", cateTotalFielderOpp, cateTotalFielderOldOpp);
        }
        else {
            updateTotal("Today", "Fielder", "my", cateTotalFielderMy, cateTotalFielderOldMy);
            updateTotal("Today", "Fielder", "opp", cateTotalFielderOpp, cateTotalFielderOldOpp);
        }
        // --------------------------------------------------------------------------------------------

        // Pitcher
        let dbPitchers = response["Pitcher"];
        // let pitchers = $("#pitcherTable tbody tr");
        pitchers.each(function () {
            let row = $(this);
            let rowPlayers = row.find(".player");
            let myPlayer = rowPlayers.eq(0).find("a");
            let oppPlayer = rowPlayers.eq(1).find("a");


            dbPitchers.forEach(element => {
                if (myPlayer.text() == element[2] && row.find(".position").text() != "BN") {
                    hasValuePitcherMy = true;
                    for (let i = 0; i < 18; i++) {

                        let current = $(this).children().eq(i + 1);
                        updateSingle("Pitcher", current, i, element, cateTotalPitcherMy, cateTotalWeeklyStatsMy);
                    }
                }

                else if (oppPlayer.text() == element[2] && row.find(".position").text() != "BN") {
                    hasValuePitcherOpp = true;
                    // postion, type, empty不處理
                    for (let i = 0; i < 18; i++) {

                        let current = $(this).children().eq(i + 21);
                        updateSingle("Pitcher", current, i, element, cateTotalPitcherOpp, cateTotalWeeklyStatsOpp);
                    }
                }
            });
        });

        // 每個球員加總完後，才觀察Total的差異
        if (!hasValuePitcherMy && !hasValuePitcherOpp) {
            for (let i = 0; i < 18; i++) {
                totalPitcher.children().eq(i + 1).text("-");
                totalPitcher.children().eq(i + 21).text("-");
            }
        }
        else if (hasValuePitcherMy && !hasValuePitcherOpp) {
            updateTotal("Today", "Pitcher", "my", cateTotalPitcherMy, cateTotalPitcherOldMy);
        }
        else if (!hasValuePitcherMy && hasValuePitcherOpp) {
            updateTotal("Today", "Pitcher", "opp", cateTotalPitcherOpp, cateTotalPitcherOldOpp);
        }
        else {
            updateTotal("Today", "Pitcher", "my", cateTotalPitcherMy, cateTotalPitcherOldMy);
            updateTotal("Today", "Pitcher", "opp", cateTotalPitcherOpp, cateTotalPitcherOldOpp);
        }

        updateTotal("Weekly", true, "my", cateTotalWeeklyStatsMy, cateTotalWeeklyStatsOldMy);
        updateTotal("Weekly", true, "opp", cateTotalWeeklyStatsOpp, cateTotalWeeklyStatsOldOpp);
        compareWeekly();

        $(".positive").animate({
            backgroundColor: "#53c488",
        }, 1000, function () {
            if ($(this).hasClass("win")) {
                $(this).animate({
                    backgroundColor: "#ecf8ff",
                }, 1000, function () {
                    $(this).removeClass("positive");
                    $(this).removeClass("win");
                });
            }
            else {
                $(this).animate({
                    backgroundColor: "white",
                }, 1000, function () {
                    $(this).removeClass("positive");
                })
            }
        });

        $(".negative").animate({
            backgroundColor: "#ff5c5c",
        }, 1000, function () {
            if ($(this).hasClass("win")) {
                $(this).animate({
                    backgroundColor: "#ecf8ff",
                }, 1000, function () {
                    $(this).removeClass("negative");
                    $(this).removeClass("win");
                });
            }
            else {
                $(this).animate({
                    backgroundColor: "white",
                }, 1000, function () {
                    $(this).removeClass("negative");
                })
            }
        });


    })
})