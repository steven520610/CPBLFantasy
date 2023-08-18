$(document).ready(function () {
    $("#login").click(function (e) {
        e.preventDefault()
        let account = $("#account").val();
        let password = $("#password").val();
        let send = { "account": account, "password": password };

        $.ajax({
            url: "/login",
            type: "POST",
            data: JSON.stringify(send),
            dataType: "json",
            contentType: "application/json",
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