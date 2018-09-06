//Zigbee related libraries
var ZShepherd = require('zigbee-shepherd');
var zserver = new ZShepherd('/dev/ttyACM0');

//REST api library
var express = require('express');
var rest = express();

//Vars
const timeOut = 255; //Connection timeout is disabled if value is set to 255
const listenPort = 3000;
var isOnline = false;
var osramBulb; //OSRAM Lightify Tunable White 60 // A19 Bulb
//Alcance médio da lâmpada com o módulo zigbee Texas Instruments CC2531
//de 3 a 4 metros com visada direta da lâmpada para o módulo.
//Device id: 0x84182600000203a4

//Server is ready
zserver.on('ready', function () {
    console.log('[zServer]Zigbee server is ready! Allow devices to join the network within '+timeOut+' secs.');
    console.log('[zServer]Waiting for incoming clients or messages...');
    zserver.permitJoin(timeOut);
});

//While joining is allowed
zserver.on('permitJoining', function (joinTimeLeft) {
    if(joinTimeLeft % 30 == 0){
        console.log('[zServer]Network join timer: '+joinTimeLeft);
    }
});

//Status switch
zserver.on('ind', function (msg) {
    switch (msg.type) {
        case 'devIncoming':
            //devIncoming: novo dispositivo quer se associar ao servidor
            console.log('[zServer]Device: ' + msg.data + ' joining the network!');

            msg.endpoints.forEach(function (device) {
                //Verifica a id do dispositivo
                if (device.devId === 258){
                    osramBulb = device;
                    console.log("[zServer]Found OSRAM Bulb!");
                    console.log(device.dump());
                    //Le informacoes do dispositivo como keepalive
                    setInterval(pingDevice, 3000);
                    isOnline = true;
                } else {
                    console.log('[zServer]ERRO: Objeto não suportado! [id: '+device.devId+' ]');
                }

            });

            break;

        default:
            console.log('Tipo do callback não definido! > '+msg.type)
            break;
    }
});

//Desativa a lâmpada ao receber um post request
rest.post('/turnOff', function(req, res){
    //Analisa se a lâmpada foi conectada corretamente
    if(osramBulb){
        console.log("[zServer]Recebido POST request para desligar a lâmpada!")
        osramBulb.functional('genOnOff', 'off', {}, function (err) {
            if(!err){
                res.send(true);
            }else{
                res.send(false);
            }
        });
    }else{
        res.send(false);
    }
});

function pingDevice(){
    if(osramBulb){
        osramBulb.read('genOnOff', 'toggle', function (err, data) {
            if(err){
                if(isOnline){
                    console.log('[zServer]Lamp is now offline!');
                    isOnline = false;
                }
            }else{
                if(!isOnline){
                    console.log('[zServer]Lamp is now online!')
                    isOnline = true;
                }
            }
        });
    }
}

//Ativa a lâmpada ao receber um post request
rest.post('/turnOn', function(req, res){
    //Analisa se a lâmpada foi conectada corretamente
    if(osramBulb){
        console.log("[zServer]Recebido POST request para ligar a lâmpada!")
        osramBulb.functional('genOnOff', 'on', {}, function (err) {
            if(!err){
                res.send(true);
            }else{
                res.send(false);
            }
        });
    }else{
        res.send(false);
    }
});

//Inicia o servidor de zigbee
zserver.start(function (err) {
    if (err)
        console.log(err);
});

//Get de teste
rest.get('/', function(req, res){
    if(isOnline){
        res.send('1');
    }else{
        res.send('0');
    }
});

//Inicia o listener para receber POSTs e GETs
rest.listen(listenPort);
