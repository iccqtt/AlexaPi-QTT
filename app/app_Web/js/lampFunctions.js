var counter = 0;
function changecolorOn(){
  document.getElementById("text_status").innerHTML = "SmartLamp is On!"
  document.getElementById("lala").src = "./images/icon_on.png"
  document.getElementById("border_1").className = "polaroid3"
  document.getElementById("border_2").className = "containered3"
  document.getElementById("informationText").innerHTML = "Status: Online"
  document.getElementById("informationText").classList.remove('alert-danger');
  document.getElementById("informationText").classList.remove('text-danger');
  document.getElementById("informationText").classList.add('text-info');
  document.getElementById("informationText").classList.add('alert-info');

}
function changecolorOff(){
  document.getElementById("lala").src = "./images/icon_off.png"
  document.getElementById("border_1").className = "polaroid"
  document.getElementById("border_2").className = "containered"
  document.getElementById("text_status").innerHTML = "SmartLamp is Off!"
  document.getElementById("informationText").innerHTML = "Status: Online"
  document.getElementById("informationText").classList.remove('alert-danger');
  document.getElementById("informationText").classList.remove('text-danger');
  document.getElementById("informationText").classList.add('alert-info');
  document.getElementById("informationText").classList.add('text-info');
}
function changecolorOffline(){
  var checkbox = document.querySelector('input[type="checkbox"]');
  checkbox.checked = false;
  document.getElementById("text_status").innerHTML = "SmartLamp is Offline!"
  document.getElementById("lala").src = "./images/icon_offline.png"
  document.getElementById("border_1").className = "polaroid"
  document.getElementById("border_2").className = "containered"
  document.getElementById("informationText").innerHTML = "Status: Offline"
  document.getElementById("informationText").classList.add('alert-danger');
  document.getElementById("informationText").classList.add('text-danger');
}

document.addEventListener('DOMContentLoaded', function () {
  var checkbox = document.querySelector('input[type="checkbox"]');
  checkbox.addEventListener('change', function () {
    if (checkbox.checked) {
      makePostOnLamp();
    } else {
      makePostOffLamp();
    }
    });
});

setInterval(function(){
  getLampStatus();
}, 20000);

function SelectItem(x) {
  x.classList.add('active');
}

function DeselectItem(x){
  x.classList.remove('active');
} 

function makePostOnLamp() {
  xmlhttp = new XMLHttpRequest();
 
  var URLADDRESS = window.location.href 
  IP= URLADDRESS.split("/")
  console.log("IPMEU: "+IP[2])
  var hostname = IP[2] 
  
  var url = "http://"+hostname+":3000/turnOn"
  xmlhttp.open("POST", url, true);
  xmlhttp.setRequestHeader("Content-type", "application/json");
  var parameters = JSON.stringify({"request": {
      "type": "STATUS",
      "onlinestatus": true
  }});    
  xmlhttp.onreadystatechange = function receiveResponse() {
    if (this.readyState == 4) {
        if (this.status == 200) {
            console.log("Json try:"+parameters);
            console.log("We go a response : " + this.response);
            if(this.response == "OK"){
                changecolorOn();
            }
            else{
              changecolorOffline();
              counter = 0;
            }
        } else if (this.status == 0) {
            console.log("The computer appears to be offline.");
            alert("Server is offline");
            var checkbox = document.querySelector('input[type="checkbox"]');
            checkbox.checked = false;
        } else{
            console.log("An internet error has ocurred");
        }
    }
  };
  xmlhttp.ontimeout = function (e) {
    console.log("timeout on get function");
  };
  xmlhttp.send(parameters);
  
}

function makePostOffLamp() {
  xmlhttp = new XMLHttpRequest();
  
  var URLADDRESS = window.location.href 
  IP= URLADDRESS.split("/")
  console.log("IPMEU: "+IP[2])
  var hostname = IP[2] 
  
  var url = "http://"+hostname+":3000/turnOff"
  xmlhttp.open("POST", url, true);
  xmlhttp.setRequestHeader("Content-type", "application/json");
  var parameters = JSON.stringify({"request": {
      "type": "STATUS",
      "onlinestatus": true
  }});    
  xmlhttp.onreadystatechange = function receiveResponse() {
    if (this.readyState == 4) {
        if (this.status == 200) {
            console.log("Json try:"+parameters);
            console.log("We go a response : " + this.response);
            if(this.response == "OK"){
              changecolorOff();
            }
            else{
              changecolorOffline();
              counter = 0;
            }
        } else if (this.status == 0) {
            console.log("The computer appears to be offline.");
            alert("Server is offline");
            checkbox.checked = false;
        } else{
            console.log("An internet error has ocurred");
        }
    }
  };
  xmlhttp.ontimeout = function (e) {
    console.log("timeout on get function");
  };
  xmlhttp.send(parameters);
}

function getLampStatus(){
  console.log("Checking Lamp Status");
  xmlhttp = new XMLHttpRequest();
  
  var URLADDRESS = window.location.href 
  IP= URLADDRESS.split("/")
  console.log("IPMEU: "+IP[2])
  var hostname = IP[2] 

  var url = "http://"+hostname+":3000/";
  xmlhttp.open("GET", url,true);
  xmlhttp.timeout = 3000;
  xmlhttp.onreadystatechange = function (oEvent) {  
    if (xmlhttp.readyState === 4) {  
        if (xmlhttp.status === 200) {  
          if(xmlhttp.responseText == "1"){
            console.log("lamp online");
            if(counter==0){
              alert("Lamp back online, please update it's status");
              changecolorOff();
            }
            counter = counter + 1;
          }
          else{
            console.log("lamp offline");
            //changecolorOffline();
            
            counter = 0;
          }
          console.log("correct responsed");    
        }
        else{
          console.log("not arriving correct response");
          var checkbox = document.querySelector('input[type="checkbox"]');
          checkbox.checked = false;
          changecolorOffline();
          counter = 0;
        }
    }
  };
  xmlhttp.ontimeout = function (e) {
    console.log("timeout on get function");
  };
  xmlhttp.send(null);
}

