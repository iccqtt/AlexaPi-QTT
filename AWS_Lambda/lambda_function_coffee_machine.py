"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3
import json
import os


TOPIC_TURN_ON_OFF = "qualcomm/CoffeeMachine/TurnOnOff/Android";
TOPIC_SHORT_COFFEE = "qualcomm/CoffeeMachine/ShortCoffee/Android";
TOPIC_LONG_COFFEE = "qualcomm/CoffeeMachine/LongCoffee/Android";

POSITIONED = 1
FULL = 1
MIN_LEVEL_WATER = 5
ON = 1


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def turn_coffee_machine(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
        user.
        """

    client = boto3.client('iot-data', region_name='us-west-2')

    session_attributes = {}
    card_title = "Welcome"
    should_end_session = True
    reprompt_text = None

    if 'CoffeeState' in intent['slots']:
        coffee_state = intent['slots']['CoffeeState']['value']
        if (not is_online()):
            if coffee_state == 'on' or coffee_state == 'off':
                if coffee_state == 'on':
                    client.publish(topic=TOPIC_TURN_ON_OFF, qos=1, payload=json.dumps({"state": "1"}))
                    speech_output = "The coffee machine is " + coffee_state
                    save_on_off_status(1)
                else:
                    client.publish(topic=TOPIC_TURN_ON_OFF, qos=1, payload=json.dumps({"state": "0"}))
                    speech_output = "The coffee machine is " + coffee_state
                    save_on_off_status(0)
            else:
                speech_output = "Status not recognized. Please, try again."
        else:
            speech_output = "The coffee machine is offline."
    else:
        speech_output = "Please, try again."
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# --------------- Functions that control the skill's behavior ------------------

def skill_information():
    """ Sets the color in the session and prepares the speech to reply to the
        user.
        """

    client = boto3.client('iot-data', region_name='us-west-2')

    session_attributes = {}
    card_title = "Welcome"
    should_end_session = True
    reprompt_text = None

    if(is_online()):
        speech_output = "The coffee machine is offline."
    else:
        client.publish(topic=TOPIC_TURN_ON_OFF, qos=1, payload=json.dumps({"state": "1"}))
        speech_output = "The coffee machine is on"
        save_on_off_status(1)

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_light_state_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def turn_off_coffee_machine():
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    card_title = "Session Ended"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    session_attributes = {}

    client = boto3.client('iot-data', region_name='us-west-2')
    if(is_online()):
        speech_output = "The coffee machine is offline"
    else:
        speech_output = "The coffee machine is off"
        client.publish(topic=TOPIC_TURN_ON_OFF, qos=1, payload=json.dumps({"state": "0"}))
        save_on_off_status(0)

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, None, should_end_session))


def make_coffee(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    client = boto3.client('iot-data', region_name='us-west-2')
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = None

    if is_online():
        print("Machine current state > "+str(is_online()))
        speech_output = "The coffee machine is offline!"
    elif is_on():
        speech_output = "The coffee machine is off."
    elif is_glass_positioned():
        speech_output = "There is no glass on the Coffee Machine."
    elif is_water_level_ok():
        speech_output = "There is no water to make coffee."
    elif is_coffee_level_ok():
        speech_output = "There is not enough coffee."
    elif is_busy():
        speech_output = "Please wait! The coffee machine seens to be busy."
    else:
        if 'CoffeeType' in intent['slots']:
            coffee_type = intent['slots']['CoffeeType']['value']
            if coffee_type == 'long' or coffee_type == 'short':
                if coffee_type == 'long':
                    client.publish(topic=TOPIC_LONG_COFFEE, qos=1, payload=json.dumps({"state": "1"}))
                    speech_output = "OK. Making " + coffee_type + " coffee!"
                else:
                    client.publish(topic=TOPIC_SHORT_COFFEE, qos=1, payload=json.dumps({"state": "1"}))
                    speech_output = "OK. Making " + coffee_type + " coffee!"

            else:
                speech_output = "Status not recognized. Please, try again."
        else:
            speech_output = "Please, try again."
    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def is_glass_positioned():
    glassPosition = int(os.getenv('glassposition'))
    if glassPosition == POSITIONED:
        return False
    return True


def is_water_level_ok():
    waterLevel = int(os.getenv('waterlevel'))
    if waterLevel == FULL:
        return False
    return True

def is_online():
    online = int(os.getenv('onlinestatus'))
    if(online == ON):
        return False
    return True

def is_busy():
    busy = int(os.getenv('busy'))
    if(busy == ON):
        return True
    return False

def is_coffee_level_ok():
    coffeeLevel = int(os.getenv('coffeelevel'))
    if coffeeLevel > MIN_LEVEL_WATER:
        return False
    return True

def is_on():
    on_off = int(os.getenv('on_off'))
    if on_off == ON:
        return False
    return True


# --------------- Events ------------------
def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return skill_information()


def invalid_intent():
    card_title = "Invalid Intent"
    speech_output = "Sorry! I don't know that one."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MakeCoffee":
        return make_coffee(intent, session)
    elif intent_name == "TurnCoffeeMachine":
        return turn_coffee_machine(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return turn_off_coffee_machine()
    else:
        return invalid_intent()
        #raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def save_on_off_status(status):
    on_off = status
    coffeeLevel = int(os.getenv('coffeelevel'))
    waterLevel = int(os.getenv('waterlevel'))
    glassPosition = int(os.getenv('glassposition'))
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'of/off status': on_off})

def saveCoffeeMachineStatus(request):
    waterLevel = request['water']

    glassPosition = request['glass']
    coffeeLevel = int(os.getenv('coffeelevel'))
    on_off = request['on_off']
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'water level' : waterLevel, 'coffee level' : coffeeLevel, 'glass position' : glassPosition, 'on/off status' : on_off})


def glassStatus(request):
    glassPosition = request['glass']

    waterLevel = int(os.getenv('waterlevel'))
    coffeeLevel = int(os.getenv('coffeelevel'))
    on_off = int(os.getenv('on_off'))
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'glass position' : glassPosition})


def waterStatus(request):
    waterLevel = request['water']

    glassPosition = int(os.getenv('glassposition'))
    coffeeLevel = int(os.getenv('coffeelevel'))
    on_off = int(os.getenv('on_off'))
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'water level' : waterLevel})


def coffeeStatus(request):
    coffeeLevel = request['coffee']

    waterLevel = int(os.getenv('waterlevel'))
    glassPosition = int(os.getenv('glassposition'))
    on_off = int(os.getenv('on_off'))
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'coffee level' : coffeeLevel})

def busyStatus(request):
    busyStats = request['busy']

    waterLevel = int(os.getenv('waterlevel'))
    glassPosition = int(os.getenv('glassposition'))
    on_off = int(os.getenv('on_off'))
    online_status = int(os.getenv('onlinestatus'))
    coffeeLevel = int(os.getenv('coffeelevel'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busyStats)

    return json.dumps({'busy' : busyStats})

def on_off_status(request):
    on_off = request['on_off']

    coffeeLevel = int(os.getenv('coffeelevel'))
    waterLevel = int(os.getenv('waterlevel'))
    glassPosition = int(os.getenv('glassposition'))
    online_status = int(os.getenv('onlinestatus'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, online_status, busy_status)

    return json.dumps({'of/off status' : on_off})

def online_status_f(request):
    onlineStatus = request['onlinestatus']
    waterLevel = int(os.getenv('waterlevel'))
    glassPosition = int(os.getenv('glassposition'))
    on_off = int(os.getenv('on_off'))
    coffeeLevel = int(os.getenv('coffeelevel'))
    busy_status = int(os.getenv('busy'))

    save_environment_variable(on_off, waterLevel, coffeeLevel, glassPosition, onlineStatus, busy_status)

    return json.dumps({'onlinestatus' : onlineStatus})


def save_environment_variable (on_off, waterLevel, coffeeLevel, glassPosition, onlineStatus, busyStats):
    client = boto3.client('lambda')
    client.update_function_configuration(
        FunctionName='arn:aws:lambda:us-west-2:459009673627:function:coffee-machine-function',
        Environment={
            'Variables': {
                'waterlevel': str(waterLevel),
                'glassposition': str(glassPosition),
                'coffeelevel': str(coffeeLevel),
                'on_off': str(on_off),
                'onlinestatus': str(onlineStatus),
                'busy': str(busyStats)
            }
        }
    )


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    if 'session' in event:
        print("event.session.application.applicationId=" +
            event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if ('session' in event and (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.57119d91-fb3c-487f-be53-4e7fac12fb83")):
        raise ValueError("Invalid Application ID")

    """if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])"""

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
    elif event['request']['type'] == 'UPDATE':
        return saveCoffeeMachineStatus(event['request'])
    elif event['request']['type'] == "GLASS":
        return glassStatus(event['request'])
    elif event['request']['type'] == "WATER":
        return waterStatus(event['request'])
    elif event['request']['type'] == "COFFEE":
        return coffeeStatus(event['request'])
    elif event['request']['type'] == "ON_OFF":
        return on_off_status(event['request'])
    elif event['request']['type'] == "ONLINE":
        return online_status_f(event['request'])
    elif event['request']['type'] == 'BUSY':
        return busyStatus(event['request'])
