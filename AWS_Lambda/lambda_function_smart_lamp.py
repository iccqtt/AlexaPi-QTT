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


TOPIC_TURN_ON_OFF_LAMP = "qualcomm/TurnOnOffLamp"

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


def turn_light_stand(intent, session):
	""" Sets the color in the session and prepares the speech to reply to the
		user.
		"""

	client = boto3.client('iot-data', region_name='us-west-2')

	session_attributes = {}
	card_title = "Welcome"
	should_end_session = True
	reprompt_text = None

	if 'LampState' in intent['slots']:
		lamp_state = intent['slots']['LampState']['value']
		if(is_online()):
			if lamp_state == 'on' or lamp_state == 'off':
				if lamp_state == 'on':
					client.publish(topic=TOPIC_TURN_ON_OFF_LAMP, qos=1, payload=json.dumps({"state": "1"}))
					speech_output = "The kitchen lamp is " + lamp_state
					# save_on_off_status(1)
				else:
					client.publish(topic=TOPIC_TURN_ON_OFF_LAMP, qos=1, payload=json.dumps({"state": "0"}))
					speech_output = "The kitchen lamp is " + lamp_state
					# save_on_off_status(0)

			else:
				speech_output = "Status not recognized. Please, try again."
		else:
			speech_output = "The kitchen lamp is offline!"
	else:
		speech_output = "Please, try again."
	return build_response(session_attributes,
						build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# --------------- Functions that control the skill's behavior ------------------
def turn_off_lamp_stand():
	""" Sets the color in the session and prepares the speech to reply to the
		user.
		"""

	client = boto3.client('iot-data', region_name='us-west-2')

	session_attributes = {}
	card_title = "Welcome"
	should_end_session = True
	reprompt_text = None

	if(is_online()):
		client.publish(topic=TOPIC_TURN_ON_OFF_LAMP, qos=1, payload=json.dumps({"state": "0"}))
		speech_output = "The kitchen lamp is off"
	else:
		speech_output = "The kitchen lamp is offline"

    #save_on_off_status(1)

	return build_response(session_attributes,
						build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))



def turn_on_lamp_stand():
	""" Sets the color in the session and prepares the speech to reply to the
		user.
		"""

	client = boto3.client('iot-data', region_name='us-west-2')

	session_attributes = {}
	card_title = "Welcome"
	should_end_session = True
	reprompt_text = None

	if(is_online()):
		client.publish(topic=TOPIC_TURN_ON_OFF_LAMP, qos=1, payload=json.dumps({"state": "1"}))
		speech_output = "The kitchen lamp is on"
	else:
		speech_output = "The kitchen lamp is offline"


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
	return turn_on_lamp_stand()


def invalid_intent():
	card_title = "Invalid Intent"
	speech_output = "Sorry! I don't know that one."
	# Setting this to true ends the session and exits the skill.
	should_end_session = False
	return build_response({}, build_speechlet_response(
		card_title, speech_output, None, should_end_session))


def on_intent(intent_request, session):
	""" Called when the user specifies an intent for this skill """

	print("on_intent requestId=" + intent_request['requestId'] +
		  ", sessionId=" + session['sessionId'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	# Dispatch to your skill's intent handlers

	if intent_name == "TurnLamp":
		return turn_light_stand(intent, session)
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return turn_off_lamp_stand()
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

def online_status(request):
	onlineStatus = request['onlinestatus']
	save_environment_variable(onlineStatus)
	return json.dumps({'onlinestatus' : onlineStatus})

def save_environment_variable (status):
    client = boto3.client('lambda')
    client.update_function_configuration(
        FunctionName='arn:aws:lambda:us-west-2:459009673627:function:lamp-stand-function',
        Environment={
            'Variables': {
                'onlinestatus': str(status)
            }
        }
    )

def is_online():
    online = int(os.getenv('onlinestatus'))
    if(online == ON):
        return True
    return False

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
			"amzn1.ask.skill.8aac266b-1344-4f21-b994-447659a1cf55")):
		raise ValueError("Invalid Application ID")

	"""if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']},
						   event['session'])"""

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "TurnLamp":
		return turn_on_lamp_stand(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])
	elif event['request']['type'] == "STATUS":
		return online_status(event['request'])
