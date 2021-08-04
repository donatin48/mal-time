window.onload=function(){
var form = document.getElementById("form");
if(form){
    var user = document.getElementById("user");
    form.addEventListener("submit", function (e){
        e.preventDefault();
        if(user.value){
            // window.location.href += "user/" + user.value.trim() + "/";
            window.location.href = "https://lelab.ml/user/" + user.value.trim() + "/";
        }
    })
}

var set = document.getElementById("set")
if (set) {set.addEventListener("click",SetProfile)}

function SetProfile(){
    localStorage.clear();
    username = window.location.href.slice(22,-1);
    localStorage.setItem('profile', username);
    ApplyProfile()
}

if(localStorage.hasOwnProperty('profile')){
    ApplyProfile()
}

function ApplyProfile(){
    let username = localStorage.getItem('profile');
    document.getElementById("btnprofile").href = "https://lelab.ml/user/" + username + "/";
}

}


