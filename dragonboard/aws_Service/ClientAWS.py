from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging

# Configure authentication variables path
host = "a3ia6ywt1k1290.IOT.us-west-2.amazonaws.com"
rootCAPath = "authenticated/root-CA.crt"
certificatePath = "authenticated/23985f5177-certificate.pem.crt"
privateKeyPath = "authenticated/23985f5177-private.pem.key"
clientID = "COFFEE_MACHINE_QTT"

def createClient():

    # Configure logging
    #logger = logging.getLogger("AWSIoTPythonSDK.core")
    #logger.setLevel(logging.INFO)
    #streamHandler = logging.StreamHandler()
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #streamHandler.setFormatter(formatter)
    #logger.addHandler(streamHandler)

    # Initialize MQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientID)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return myAWSIoTMQTTClient
