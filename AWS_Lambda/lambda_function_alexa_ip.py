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


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):

    ip1,ip2,ip3,ip4 = output.split(".")

    return {
        'outputSpeech': {
            "ssml": "<speak>"\
                        "Your ip address is: "\
						"<say-as interpret-as=\"spell-out\">"\
							+ip1+\
						"</say-as>.<break time= \"150ms\"/>"\
						"<say-as interpret-as=\"spell-out\">"\
							+ip2+\
						"</say-as>.<break time= \"150ms\"/>"\
						"<say-as interpret-as=\"spell-out\">"\
							+ip3+\
						"</say-as>.<break time= \"150ms\"/>"\
						"<say-as interpret-as=\"spell-out\">"\
							+ip4+\
						"</say-as>."\
					"</speak>",
            'type': "SSML"
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


# --------------- Functions that control the skill's behavior ------------------


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def cancel_intent():
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    card_title = "Session Ended"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    session_attributes = {}
    speech_output = "The skill has been closed"

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, None, should_end_session))


def sendIP(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    reprompt_text = None

    ip = os.getenv('ip')
    speech_output = ip

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------
def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    intent = "intentIP"

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    # redirect to main function to tell my ip
    return invalid_intent()


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
    if intent_name == "intentIP":
        return sendIP(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return cancel_intent()
    else:
        return invalid_intent()
        # raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def save_ip(request):
    ip = request['address']
    save_environment_variable(ip)

    responseBody = {
        "ip": ip
    }

    response = {
        "statusCode": 200,
        "headers": {
            "my_header": "my_value"
        },
        "body": responseBody,
        "isBase64Encoded": False
    }

    return response


def save_environment_variable(IP):
    client = boto3.client('lambda')
    client.update_function_configuration(
        FunctionName='arn:aws:lambda:us-west-2:459009673627:function:alexa_ip',
        Environment={
            'Variables': {
                'ip': str(IP),
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
            "amzn1.ask.skill.dab0b944-71a8-4266-8fee-4aeb6b3d80be")):
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
    elif event['request']['type'] == "IP":
        return save_ip(event['request'])
