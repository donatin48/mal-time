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

var ctx = document.getElementById('graph1');
if(ctx){

var username = document.getElementById("username").innerText
fetch("https://lelab.ml/api/v1/username/" + username )
.then(function(response) {
    return response.json();
})
.then(function(jsonResponse) {
    var data = jsonResponse 
    console.log(data)
});


const labels = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
];

const data = {
    labels: labels,
    datasets: [{
        label: 'test',
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: [0, 10, 5, 2, 20, 30, 45],
    }]
};

const config = {
    type: 'line',
    data,
    options: {}
    };

var graph1 = new Chart(ctx,config);



}
}

