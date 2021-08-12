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

var ctx1 = document.getElementById('graph1');
var ctx2 = document.getElementById('graph2');
if(ctx1){
var username = document.getElementById("username").innerText

// function getdata(){
//     fetch("https://lelab.ml/api/v1/username/" + username)
//     .then(function(response) {
//         return response.json();})
//     .then(function(jsonResponse) {
//         mal_data = jsonResponse 
//         console.log(mal_data)
//     });
//     return mal_data
// }

fetch('https://lelab.ml/api/v1/username/' + username)
  .then(jsonData => jsonData.json())
  .then(mal_data => printIt(mal_data))

let printIt = (mal_data) => {
console.log(mal_data)



const labels = Array.from({length: mal_data["data"].length}, (_, i) => i + 1)

var episodes_watched = []
var completed = []
for (c of mal_data["data"]){
    episodes_watched.push(c["episodes_watched"])
    completed.push(c["completed"])
}
console.log(episodes_watched,completed);
var data = {
    labels: labels,
    datasets: [{
        label: 'episodes_watched',
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: episodes_watched,
    }]
};

var config = {
    type: 'line',
    data,
    options: {}
    };

var graph1 = new Chart(ctx1,config);

var data = {
    labels: labels,
    datasets: [{
        label: 'completed',
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: completed,
    }]
};
var config2 = {
    type: 'line',
    data,
    options: {}
};

var graph2 = new Chart(ctx2,config2);


}
}
}

