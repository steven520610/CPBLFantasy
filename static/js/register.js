$(document).ready(function () {
    let check = false;
    $("#validate").click(function () {
        let account = $("#account").val();
        if (!account) {
            $("#validateInfo").text("帳號不可為空白！");
        }
        else {
            let send = { "account": account };
            $.ajax({
                url: "/register",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify(send),
                dataType: "json",
                success: function (response) {
                    if (response["replicated"]) {
                        $("#validateInfo").text("此帳號已存在！");
                        check = false;
                    }
                    else {
                        $("#validateInfo").text("可使用此帳號！");
                        check = true;
                    }
                }
            });
        }
    });

    $("#register").click(function () {
        if (!check) {
            $("#replicateInfo").text("尚未檢查帳號或帳號已存在！");
        }
        else {
            let account = $("#account").val();
            let password = $("#password").val();
            if (!account || !password) {
                $("replicateInfo").text("帳號或密碼不可為空白！");
            }

            else {
                let team = $("input[name='team']:checked").val();
                console.log(team);
                let send = { "account": account, "password": password, "team": team };
                $.ajax({
                    url: "/register",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify(send),
                    dataType: "json",
                    success: function (response) {
                        if (response["success"]) {
                            const url = URL(response["redirect"], window.location.origin);
                            window.location.href = url.href;
                        }
                    }
                });
            }
        }
    });
})