(function () {
    $(document).ready(function(){
        
        var URLADDRESS = window.location.href 
        IP= URLADDRESS.split("/")
        console.log("IPMEU: "+IP[2])
        var hostname = IP[2]    

        setInterval(function(){
            //getting information
            $.get("http://"+hostname+":5000/coffeeStatus", function(data, status){

                var obj = JSON.parse(data);
        
                if(obj.request.water){
                    document.getElementById("statusCoffee").innerHTML = "Full";
                    document.getElementById("statusCoffee").classList.remove('alert-danger');
                    document.getElementById("statusCoffee").classList.remove('text-danger');
                    document.getElementById("statusCoffee").classList.add('alert-success');
                    document.getElementById("statusCoffee").classList.add('text-success');
                }else{
                    document.getElementById("statusCoffee").innerHTML = "Empty";
                    document.getElementById("statusCoffee").classList.add('alert-danger');
                    document.getElementById("statusCoffee").classList.add('text-danger');
                    document.getElementById("statusCoffee").classList.remove('alert-success');
                    document.getElementById("statusCoffee").classList.remove('text-success');
                }
                
                if(obj.request.glass){
                    document.getElementById("textGlass").innerHTML = "The cup is positioned";
                    document.getElementById("textGlass").classList.remove('text-danger');
                    document.getElementById("textGlass").classList.add('text-success');
                    document.getElementById("imageGlass").src = "images/icon_coffee_glass.png";
                }else{
                    document.getElementById("textGlass").innerHTML = "The cup is not positioned";
                    document.getElementById("textGlass").classList.add('text-danger');
                    document.getElementById("textGlass").classList.remove('text-success');
                    document.getElementById("imageGlass").src = "images/icon_no_coffee_glass.png";
                }

                if(obj.request.on_off){
                    document.getElementById('switchButton').checked = true;
                }else{
                    document.getElementById('switchButton').checked = false;
                }

            });
        }, 2000);

        //button long coffee
        $("#long").click(function(){

            document.getElementById("informationText").innerHTML = "Wait response...";
            $.get("http://"+hostname+":5000/coffeeLong", function(data, status){

                console.log(data);
                
                switch(data){
                    case "OK":
                        document.getElementById("informationText").innerHTML = "Making long coffee!";
                        break;
                    case "IsOff":
                        document.getElementById("informationText").innerHTML = "It's not possible, the coffee machine is off.";
                        break;
                    case "IsOffline":
                        document.getElementById("informationText").innerHTML = "It's not possible, the coffee machine is offline.";
                        break;
                    case "NoWater":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no water.";
                        break;
                    case "NoGlass":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no glass.";
                        break; 
                    case "NoCoffee":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no coffee.";
                        break;
                    case "Busy":
                        document.getElementById("informationText").innerHTML = "The coffee machine is busy";
                        break;
                    default:
                        document.getElementById("informationText").innerHTML = "There is some problem with server.";
                }
            });
        });

        $("#short").click(function(){

            document.getElementById("informationText").innerHTML = "Wait response...";

            $.get("http://"+hostname+":5000/coffeeShort", function(data, status){
                console.log(data);
                switch(data){
                    case "OK":
                        document.getElementById("informationText").innerHTML = "Making short coffee!";
                        break;
                    case "IsOff":
                        document.getElementById("informationText").innerHTML = "It's not possible, the coffee machine is off.";
                        break;
                    case "IsOffline":
                        document.getElementById("informationText").innerHTML = "It's not possible, the coffee machine is offline.";
                        break;
                    case "NoWater":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no water.";
                        break;
                    case "NoGlass":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no glass.";
                        break; 
                    case "NoCoffee":
                        document.getElementById("informationText").innerHTML = "It's not possible, there is no coffee.";
                        break;
                    case "Busy":
                        document.getElementById("informationText").innerHTML = "The coffee machine is busy";
                        break;
                    default:
                        document.getElementById("informationText").innerHTML = "There is some problem with server.";
                }
            });
        });

        $("#switchButton").click(function(){

            document.getElementById("informationText").innerHTML = "Wait response...";

            var elm = document.getElementById('switchButton');

            if(elm.checked == true){
                elm.checked = true;
                $.get("http://"+hostname+":5000/turnOn", function(data, status){
                    document.getElementById("informationText").innerHTML = "Coffee Machine is on.";
                });
                
            }else{
                elm.checked = false;
                $.get("http://"+hostname+":5000/turnOff", function(data, status){
                    document.getElementById("informationText").innerHTML = "Coffee Machine is off.";
                });
            }
        });
    });
})();