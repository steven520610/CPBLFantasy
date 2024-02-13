$(document).ready(function () {
    $("#login").click(function (e) {
        /* 防止form的提交行為，在html是設定成提交到 
           同樣是自己的login.html內
        */
        e.preventDefault()
        let account = $("#account").val();
        let password = $("#password").val();
        let send = { "account": account, "password": password };

        $.ajax({
            url: "/login",
            type: "POST",
            // 先定義HTTP協議中，標頭所需要的媒體類型(MIME)
            // 不同的媒體類型，接收方會有不同的處理方法。
            contentType: "application/json",
            data: JSON.stringify(send),
            // Flask中的jsonify function，會將contentType自動設定為application/json
            dataType: "json",
            success: function (response) {
                if (response["success"]) {
                    const url = new URL(response["redirect"], window.location.origin);
                    if (response["admin"]) {
                        window.location.href = url.href;
                    }
                    else {
                        window.location.href = url.href + "/" + response["id"];
                    }
                }
                else {
                    alert("帳號或密碼錯誤！");
                }
            }
        })
    })
}) 