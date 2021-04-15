window.onload=function(){
    var form = document.getElementById("form");
    if(form){
        var user = document.getElementById("user");
        form.addEventListener("submit", function (e){
            e.preventDefault();
            if(user.value){
                window.location.href += "users/" + user.value;
            }
        })
    }
}

