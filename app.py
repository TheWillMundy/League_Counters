from flask import Flask
from flask_ask import Ask, statement, question, session
from fuzzywuzzy import process
import inflect
import json
import time
import unidecode

inflect_engine = inflect.engine()

app = Flask(__name__)
ask = Ask(app, "/champion_counters")

def match_champion_name(spoken_name):
    allChampions = get_all_champions()
    matched_champion = process.extractOne(spoken_name, allChampions)
    return matched_champion

def get_all_champions():
    # JSON is hosted at myjson.com as well just in case
    # url = 'https://api.myjson.com/bins/tkg0v'
    with open('allChampions.json') as json_data:
        data = json.load(json_data)
        allChampions = [unidecode.unidecode(listing['Champion Names']) for listing in data]
        return allChampions

def get_counters(champion):
    with open('allChampions.json') as json_data:
        data = json.load(json_data)
        counters = []
        counterLocations = []
        for listing in data:
            if (unidecode.unidecode(listing['Champion Names']) == champion):
                for i in range(1, 7):
                    currentCounter = inflect_engine.ordinal(i)
                    counterKey = currentCounter + " Counter"
                    #Gets Champion
                    fullUrl = listing[counterKey]
                    counterChampion = fullUrl.split("http://lolcounter.com/champions/")
                    counters.append(counterChampion[1])
                    #Gets Location
                    counterKey = currentCounter + " Counter Location"
                    counterLocation = listing[counterKey]
                    counterLocations.append(counterLocation)
        counters_and_locations = zip(counters, counterLocations)
        return counters_and_locations

def get_strong_against(champion):
    with open('allChampions.json') as json_data:
        data = json.load(json_data)
        champion_counters = []
        locations = []
        for listing in data:
            if (unidecode.unidecode(listing['Champion Names']) == champion):
                for i in range(1,7):
                    currentStrongAgainst = inflect_engine.ordinal(i)
                    strongAgainstKey = currentStrongAgainst + " Strong Against"
                    #Gets Champion
                    fullUrl = listing[strongAgainstKey]
                    strongAgainstChampion = fullUrl.split("http://lolcounter.com/champions/")
                    champion_counters.append(strongAgainstChampion[1])
                    #Gets Location
                    strongAgainstKey = currentStrongAgainst + " Strong Against Location"
                    strongAgainstLocation = listing[strongAgainstKey]
                    locations.append(strongAgainstLocation)
        champs_and_locations = zip(champion_counters, locations)
        return champs_and_locations

def get_partners(champion):
    with open('allChampions.json') as json_data:
        data = json.load(json_data)
        partners = []
        for listing in data:
            if (unidecode.unidecode(listing['Champion Names']) == champion):
                for i in range(1, 7):
                    currentPartner = inflect_engine.ordinal(i)
                    partnerKey = currentPartner + " Good Partner"
                    #Gets Champion
                    fullUrl = listing[partnerKey]
                    partnerChampion = fullUrl.split("http://lolcounter.com/champions/")
                    try:
                        if (i == 6):
                            partnerChampion[1] = 'and ' + partnerChampion[1]
                        partners.append(partnerChampion[1])
                    except:
                        partners.append('None Listed')
        return partners

def get_counter_tips(champion):
    with open('allChampions.json') as json_data:
        data = json.load(json_data)
        counter_tips = []
        for listing in data:
            if (unidecode.unidecode(listing['Champion Names']) == champion):
                for i in range(1, 5):
                    currentTip = inflect_engine.number_to_words(i)
                    tipKey = "Counter Tip " + currentTip.title()
                    tipText = listing[tipKey]
                    counter_tips.append(tipText)
        return counter_tips

@app.route('/')
def homepage():
    return 'Greetings, this is an Alexa Skill. Now shoo, let the other requests have their turn.'

@ask.launch
def start_skill():
    welcome_message = "<speak> Hi there! Give me a champion, any champion, and ask for their counters, what champions they are strong against, or general tips on countering them. </speak>"
    return question(welcome_message)

@ask.intent("CounterIntent")
def share_counters(spoken_champion):
    #First, match spoken champ to champion in list
    champion = match_champion_name(spoken_champion)
    champion = champion[0]
    counters_dict = get_counters(champion)
    firstMessage = []
    for i in range(3):
        if (counters_dict[i][1] == "General"):
            firstMessage.append("{}'s {} counter is {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0]))
        else:
            firstMessage.append("{}'s {} counter is {}, primarily in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0], counters_dict[i][1]))
    firstMessage = '<break time="0.5s"/> '.join(firstMessage)
    firstMessage = "<speak> " + firstMessage + " Do you want more counters, or would you like {}'s lane partners? </speak>".format(champion)
    #For use after testing
    session.attributes['counters_dict'] = counters_dict
    session.attributes['champion'] = champion
    return question(firstMessage)

# @ask.intent("ContinueCounters")
# def continue_counters():
#     counters_dict = session.attributes['counters_dict']
#     champion = session.attributes['champion']
#     firstMessage = []
#     for i in range(3, 6):
#         if (counters_dict[i][1] == "General"):
#             firstMessage.append("{}'s {} counter is {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0]))
#         else:
#             firstMessage.append("{}'s {} counter is {}, primarily in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0], counters_dict[i][1]))
#     firstMessage = '<break time="0.5s"/> '.join(firstMessage)
#     firstMessage = "<speak> " + firstMessage + " Would you like {}'s lane partners now? </speak>".format(champion)
#     return question(firstMessage)

@ask.intent("Continue")
def continue_counters_or_strong_against():
    if('counters_dict' in session.attributes):
        return continue_counters()
    else:
        return continue_strong_against()
    return exit_app()
def continue_counters():
    counters_dict = session.attributes['counters_dict']
    champion = session.attributes['champion']
    firstMessage = []
    for i in range(3, 6):
        if (counters_dict[i][1] == "General"):
            firstMessage.append("{}'s {} counter is {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0]))
        else:
            firstMessage.append("{}'s {} counter is {}, primarily in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), counters_dict[i][0], counters_dict[i][1]))
    firstMessage = '<break time="0.5s"/> '.join(firstMessage)
    firstMessage = "<speak> " + firstMessage + " Would you like {}'s lane partners now? </speak>".format(champion)
    return question(firstMessage)
def continue_strong_against():
    strong_against_dict = session.attributes['strong_against_dict']
    champion = session.attributes['champion']
    firstMessage = []
    for i in range(3, 6):
        if (strong_against_dict[i][1] == "General"):
            firstMessage.append("{}'s {} favorable matchup is against {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0]))
        else:
            firstMessage.append("{}'s {} favorable matchup is against {}, primarily when in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0], strong_against_dict[i][1]))
    firstMessage = '<break time="0.5s"/> '.join(firstMessage)
    firstMessage = "<speak> " + firstMessage + " Would you like {}'s lane partners now? </speak>".format(champion)
    return question(firstMessage)
def exit_app():
    goodbye_text = "<speak>Ok, I hope I was of help. Good luck on Summoner's Rift!</speak>"
    return statement(goodbye_text)

@ask.intent("StrongAgainstIntent")
def share_strong_against(spoken_champion):
    #First, match spoken champ to champion in list
    champion = match_champion_name(spoken_champion)
    champion = champion[0]
    strong_against_dict = get_strong_against(champion)
    firstMessage = []
    for i in range(3):
        if (strong_against_dict[i][1] == "General"):
            firstMessage.append("{}'s {} favorable matchup is against {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0]))
        else:
            firstMessage.append("{}'s {} favorable matchup is against {}, primarily when in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0], strong_against_dict[i][1]))
    firstMessage = '<break time="0.5s"/> '.join(firstMessage)
    firstMessage = "<speak> " + firstMessage + " Do you want more favorable lane matchups for {}, or would you like {}'s lane partners? </speak>".format(champion, champion)
    #For use after testing
    session.attributes['strong_against_dict'] = strong_against_dict
    session.attributes['champion'] = champion
    return question(firstMessage)

# @ask.intent("ContinueStrongAgainst")
# def continue_strong_against():
#     strong_against_dict = session.attributes['strong_against_dict']
#     champion = session.attributes['champion']
#     firstMessage = []
#     for i in range(3, 6):
#         if (strong_against_dict[i][1] == "General"):
#             firstMessage.append("{}'s {} favorable matchup is against {}, in most lane matchups and situations. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0]))
#         else:
#             firstMessage.append("{}'s {} favorable matchup is against {}, primarily when in the {} lane. ".format(champion, inflect_engine.ordinal(i+1), strong_against_dict[i][0], strong_against_dict[i][1]))
#     firstMessage = '<break time="0.5s"/> '.join(firstMessage)
#     firstMessage = "<speak> " + firstMessage + " Would you like {}'s lane partners now? </speak>".format(champion)
#     return question(firstMessage)

@ask.intent("PartnerSoleIntent")
def share_partners(spoken_champion):
    #First, match spoken champ to champion in list
    champion = match_champion_name(spoken_champion)
    champion = champion[0]
    allPartners = get_partners(champion)
    firstMessage = "<speak> Good partner matchups for {} are ".format(champion) + ', '.join(allPartners) + "</speak>"
    print(firstMessage)
    return statement(firstMessage)

@ask.intent("PartnerFollowingIntent")
def partners():
    champion = session.attributes['champion']
    allPartners = get_partners(champion)
    if (allPartners[0] == 'None Listed'):
        firstMessage = '<speak> Sorry, our database does not currently list any lane partners for {}.</speak>'.format(champion)
    else:
        firstMessage = "<speak> Good partner matchups for {} are ".format(champion) + ', '.join(allPartners) + "</speak>"
    return statement(firstMessage)

@ask.intent("CounterTips")
def counter_tips(spoken_champion):
    champion = match_champion_name(spoken_champion)
    champion = champion[0]
    counter_tips = get_counter_tips(champion)
    responseMessage = '<speak> '
    i = 1
    try:
        print(i)
        while(len(counter_tips[i-1]) > 0):
            responseMessage += 'The {} Counter Tip for {} is <break time="0.25s"/> {} <break time="0.25s"/>'.format(inflect_engine.ordinal(i), champion, counter_tips[i-1])
            i += 1
    except:
        if (i == 1):
            return statement("<speak> Sorry, our database does not currently list any counter tips for {}.</speak>".format(champion))
    if (i == 1):
        return statement("<speak> Sorry, our database does not currently list any counter tips for {}.</speak>".format(champion))
    responseMessage += '</speak>'
    return statement(responseMessage)

@ask.intent("NoIntent")
def exit_app():
    goodbye_text = "<speak>Ok, I hope I was of help. Good luck on Summoner's Rift!</speak>"
    return statement(goodbye_text)

@ask.intent("AMAZON.HelpIntent")
def help_app():
    help_text = '<speak>Hello! Welcome to League Counters. If you give me a specific champion, I can provide you with details on what champions counter them, who the champion is strong against, and general tips that help you counter that champion. For example, you can ask me, <break time="0.25s"/> Alexa, ask League Counters for counters to Tahm Kench. This would get you the top three counters to Tahm Kench, and then you can either ask me to give you more counters to that champion, or list the lane partners for him. You can also ask me, <break time="0.25s"/> Alexa, ask League Counters, what champions does Fiddlesticks do well against. This will provide you with the top three champions that Fiddlesticks is strong against. You can then ask me to continue, or state lane partners for Fiddlesticks. To ask me about counter tips, you can say, Alexa, ask League Counters for counter tips on Ahri.</speak>'
    return question(help_text)

@ask.intent("AMAZON.StopIntent")
def stop_app():
    return statement('')

@ask.intent("AMAZON.CancelIntent")
def cancel_app():
    return statement('')

# @ask.intent("YesIntent")
# def share_headlines():
#     headlines = get_headlines()
#     headline_msg = "The current world news headlines are {}".format(headlines)
#     return statement(headline_msg)

if __name__ == '__main__':
    app.run()
