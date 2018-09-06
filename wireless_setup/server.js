var express = require('express'); //POSTs and GETs
var cors = require('cors'); //CORS
var bodyParser = require('body-parser') //Parses message body
const { exec } = require('child_process'); //Allows for bash command calls
var util = require('util')

rest = express();
rest.use(bodyParser.json());

const listenPort = 3000;

var SSID = "";
var PWD = "";
var SEC = "";
console.log("[setup] Started up.");

var corsOptions = {
	origin: '*'
}

rest.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

//Get de teste
rest.get('/', cors(corsOptions), function(req, res){
    res.send("The node setup server is up and running.");
	  console.log("[setup] Received server pool.");
});

rest.post('/ssid', cors(corsOptions), function(req, res){
    res.send("OK");
    console.log("[setup] Received network information data.");
    console.log("[setup] ├─> SSID: "+req.body.ssid);
    console.log("[setup] ├─> Password: "+req.body.password);
    console.log("[setup] └─> Security: "+req.body.security);
    SSID = req.body.ssid;
    PWD = req.body.password;
    SEC = req.body.security;
    //console.log("Content received:"+util.inspect(req.body, false, null));
    console.log("[setup] Creating new network config...");

    //Setup wireless network with informations sent by the client
	  exec("bash setup_nwk.sh "+PWD+" "+SSID+" "+SEC, (err, stdout, stderr) => {
	  if (err) {
	    // node couldn't execute the command
	    return;
	  }

	  // the *entire* stdout and stderr (buffered)
	  console.log(`${stdout}`);
	  //console.log(`stderr: ${stderr}`);
  });

});

//Inicia o listener para receber POSTs e GETs
rest.listen(listenPort);
