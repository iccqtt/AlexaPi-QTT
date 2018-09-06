function showHide(){
    if(document.getElementById('security').value=='none'){
    document.getElementById("inputPassword").style.display = 'none';
    document.getElementById("inputPassword").value='';
    document.getElementById("inputPassword").required = false;
    document.getElementById("checkbox").style.display = 'none';
    document.getElementById("check").checked = false;
    document.getElementById("inputPassword").type = 'password';
    document.getElementById("inputPasswordLabel").style.display = 'none';
    }
    else{
    document.getElementById("inputPassword").style.display = '';
    document.getElementById("inputPasswordLabel").style.display = '';
    document.getElementById("inputPassword").required = true;
    document.getElementById("checkbox").style.display = '';
    }
}

function showpassword(){
    if(document.getElementById("check").checked == true){
    document.getElementById("inputPassword").type = 'text';
    }else{
    document.getElementById("inputPassword").type = 'password';
    }
}

function makePostOnSSID() { 
    xmlhttp = new XMLHttpRequest();
    
    var URLADDRESS = window.location.href
    IP= URLADDRESS.split("/")
    console.log("IPMEU: "+IP[2])
    var hostname = IP[2] 
    
    var url = "http://"+hostname+":3000/ssid"  
    var ssidContent = document.getElementById("inputSSID").value;
    var passwordContent = document.getElementById("inputPassword").value;
    var securityContent = document.getElementById("security").value;
    //Validação rede aberta
    if (securityContent == "none"){
        //se ssid preenchido
        if (ssidContent != ""){
            passwordContent = true;
            parameters = JSON.stringify(
            {
                "ssid": ssidContent,
                "security": "none"
            }
            );
        }
    //Validação rede WPA
    }else if (securityContent == "wpa-psk"){
        //Se campos ssid e senha preenchidos
        if (ssidContent != "" && passwordContent != ""){
            parameters = JSON.stringify(
            {
                "ssid": ssidContent,
                "password": passwordContent,
                "security": securityContent
            }
            ); 
        }
    }
   
    //Se json tem conteudo faz o post
    if(ssidContent == "" || (passwordContent == "")||(securityContent == "")){
        console.log("No parameters to post")
    }
    else{
        xmlhttp.open("POST", url, true);
        xmlhttp.setRequestHeader("Content-type", "application/json");
        xmlhttp.onreadystatechange = function receiveResponse() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    console.log("Json try:"+parameters);
                    console.log("We go a response : " + this.response);
                    alert("New network configuration received\nConnect your device to the same network and ask Alexa for IP address to get access");
                } else if (this.status == 0) {
                    console.log("The computer appears to be offline. "+parameters);
                    alert("Dragonboard-410c appears to be offline.")
                } else{
                    console.log("An internet error has ocurred");
                    alert("An internet error has ocurred");
                }
            }
        };
        xmlhttp.send(parameters);
        console.log(parameters);
    }
  }

