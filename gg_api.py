# Project 1
# By:
# Mason Brachmann
# Ben McCormick
# Alberta Yoo
# Karim Noorani

### Imports ###

import json
import pandas as pd
import numpy as np
import sys
import spacy
nlp = spacy.load("en_core_web_sm", disable = ['textcat', 'lemmatizer'])
import nltk
from collections import Counter
import re
import regex
import os
import itertools

### Global Variables ###

key_word_award_mapping = {
        "best screenplay - motion picture": ["best|mejor","screenplay", "motion", "^(?!.*actor).*$", "^(?!.*actress).*$"],
        "best director - motion picture": ["best|mejor","director", "^(?!.*actor).*$", "^(?!.*actress).*$"],
        "best performance by an actress in a television series - comedy or musical" : ["best|mejor","actress", "comedy|musical", "television|tv|tele|series", "^(?!.*support).*$"],
        "best foreign language film" : ["best|mejor","foreign"],
        "best performance by an actor in a supporting role in a motion picture" : ["best|mejor","actor", "support", "motion", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television" : ["best|mejor","actress", "support", "television|tv|tele|series|film", "mini|film"],
        "best motion picture - comedy or musical" : ["best|mejor","motion", "comedy|musical", "^(?!.*actor).*$", "^(?!.*actress).*$", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best performance by an actress in a motion picture - comedy or musical" : ["best|mejor","actress", "comedy|musical", "^(?!.*support).*$", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best mini-series or motion picture made for television" : ["best|mejor","television|tv|series", "mini|film", "^(?!.*actor).*$", "^(?!.*actress).*$"],
        "best original score - motion picture" : ["best|mejor","score", "^(?!.*actor).*$", "^(?!.*actress).*$", "^(?!.*by).*$"],
        "best performance by an actress in a television series - drama" : ["best|mejor","actress", "television|tv|tele|series", "drama", "^(?!.*support).*$"],
        "best performance by an actress in a motion picture - drama" : ["best|mejor","actress", "drama", "^(?!.*support).*$", "^(?!.*series).*$"],
        "cecil b. demille award" : ["cecil|demille"],
        "best performance by an actor in a motion picture - comedy or musical" : ["best|mejor","actor", "comedy|musical", "^(?!.*support).*$", "^(?!.*series).*$", "^(?!.*tv).*$"], 
        "best motion picture - drama" : ["best|mejor","motion", "drama", "^(?!.*actor).*$", "^(?!.*actress).*$", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television" : ["best|mejor","support", "actor", "television|tv|tele|series|film", "mini|film"],
        "best performance by an actress in a supporting role in a motion picture" : ["best|mejor","actress", "support", "motion", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best television series - drama" : ["best|mejor","television|tv|series", "drama", "^(?!.*actor).*$", "^(?!.*actress).*$"],
        "best performance by an actor in a mini-series or motion picture made for television": ["best|mejor","actor", "television|tv|series", "mini|film" "^(?!.*support).*$"],
        "best performance by an actress in a mini-series or motion picture made for television" : ["best|mejor","actress", "television|tv|tele|series|film", "mini|film", "^(?!.*support).*$"],
        "best animated feature film" : ["best|mejor","animated", "film|feature"],
        "best original song - motion picture" : ["best|mejor","song", "^(?!.*actor).*$", "^(?!.*actress).*$", "^(?!.*by).*$"],
        "best performance by an actor in a motion picture - drama" : ["best|mejor","actor", "drama", "^(?!.*support).*$", "^(?!.*series).*$", "^(?!.*tv).*$"],
        "best television series - comedy or musical" : ["best|mejor","television|tv|series", "comedy|musical", "^(?!.*actor).*$", "^(?!.*actress).*$"],
        "best performance by an actor in a television series - drama" : ["best|mejor","actor", "television|tv|series", "drama", "^(?!.*support).*$"],
        "best performance by an actor in a television series - comedy or musical" : ["best|mejor","actor", "television|tv|series", "comedy|musical", "^(?!.*support).*$"],
        "golden globe hosts": ["host", "golden globes"]
        } 

awards = ["best screenplay - motion picture", "best director - motion picture",
          "best performance by an actress in a television series - comedy or musical",
          "best foreign language film", "best performance by an actor in a supporting role in a motion picture",
          "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television",
          "best motion picture - comedy or musical",
          "best performance by an actress in a motion picture - comedy or musical",
          "best mini-series or motion picture made for television",
          "best original score - motion picture", "best performance by an actress in a television series - drama",
          "best performance by an actress in a motion picture - drama", "cecil b. demille award",
          "best performance by an actor in a motion picture - comedy or musical", "best motion picture - drama",
          "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television",
          "best performance by an actress in a supporting role in a motion picture", "best television series - drama",
          "best performance by an actor in a mini-series or motion picture made for television",
          "best performance by an actress in a mini-series or motion picture made for television",
          "best animated feature film", "best original song - motion picture",
          "best performance by an actor in a motion picture - drama", "best television series - comedy or musical",
          "best performance by an actor in a television series - drama",
          "best performance by an actor in a television series - comedy or musical"] 

tokens_to_ignore = ["RT", "@", "golden globe", "goldenglobe", "globe", "globes", "golden", "hosts", "http", "#", "presentan", "globo", "wife", "y"]
potential_people_answers_to_ignore = ["hbo", "god", "motion picture", "winner", "award", "tv", "drama", "musical", "comedy", "actor", "actress", "movie", "honor", "star"]
potential_media_answers_to_ignore = []
### Helper Functions ###

###Sequence to Get Potential Answers
def getSolutionsFromPositions(doc, pos):
    #### This code will find take the doc and return a list of pos search that concates indices that are concurrent
    #### This idea was taken from https://stackoverflow.com/questions/63450423/how-to-find-proper-noun-using-spacy-nlp by user T. Jeanneau
    consecutives = []
    current = []
    for elt in pos:
        if len(current) == 0:
            current.append(elt)
        else:
            if current[-1] == elt - 1:
                current.append(elt)
            else:
                consecutives.append(current)
                current = [elt]
        if (len(current) != 0):
            consecutives.append(current)
    if ([doc[consecutive[0]:consecutive[-1]+1] for consecutive in consecutives] is None):
        return []
    else:
        return [doc[consecutive[0]:consecutive[-1]+1] for consecutive in consecutives]
    
### Checks if the tweet is relevant
def checkKeyWords(key_word_award_mapping, tweet):
    awards = []
    for key, value in key_word_award_mapping.items():
        go = True
        for i in value:
            if not bool(re.search(i, tweet)):
                go = False
        if go:
            awards.append(key)
    return awards
    
### Updates Host Dictionary
def updateHostDictionary(doc, tweet, hosts):  
    if ("host" in tweet and ("golden" in tweet or "globe" in tweet)):
        pos = [tok.i for tok in doc if (tok.pos_ == "PROPN" and not any(i in tok.text.lower().split() for i in tokens_to_ignore))]
        properPronouns = getSolutionsFromPositions(doc, pos)
        # Only want Phrases with 2-3 words (to represent a full name)
        for h in (properPronouns):
            potential_host = h.text.lower()
            if not checkIfPerson(h):
                continue
            if potential_host in hosts:
                hosts[potential_host] += 1
            else:
                hosts[potential_host] = 1
    return hosts

### Updates AwardNames Dictionary
def updateAwardNamesDictionary(doc, tweet, awardNames):
    if ("best " in tweet and ("dress" not in tweet or "speech" not in tweet)):                    
        nouns = ["PROPN", "NOUN"]
        pos = [tok.i for tok in doc if ((tok.pos_ in nouns) or (tok.pos_ == "ADJ" and tok.text.lower() == "best")) and not any(i in tok.text.lower().split() for i in tokens_to_ignore)]
        words = getSolutionsFromPositions(doc, pos)
        for a in (words):
            potential_award_name = a.text.lower()
            if (potential_award_name[0:5] != "best "):
                continue
            if potential_award_name in awardNames:
                awardNames[potential_award_name] += 1
            else:
                awardNames[potential_award_name] = 1
    return awardNames

### Updates Winners Dictionary
def updateWinnersDictionary(doc, tweet, winners, matches):
    if (("won" in tweet.lower() or "congrat" in tweet.lower() or "winner" in tweet.lower() or "goes to" in tweet.lower()) and ("best" in tweet.lower() or "cecil" in tweet.lower())):
        for award in matches:
            movies_tv_pos = ["PROPN", "NOUN", "ADJ", "AUX", "VERB"]
            if ("act" in award or "cecil" in award):
                pos = [tok.i for tok in doc if (tok.pos_ == "PROPN" and not any(i in tok.text.lower().split() for i in tokens_to_ignore))] 
            else:
                pos = [tok.i for tok in doc if ((tok.pos_ in movies_tv_pos or tok.text.lower() == "the" or tok.text.lower() == "of") and not any(i in tok.text.lower().split() for i in tokens_to_ignore))]            
            properPronouns = getSolutionsFromPositions(doc, pos)
            for h in (properPronouns):
                if any(i in h.text.lower() for i in potential_people_answers_to_ignore):
                    continue
                if (h.text.lower() in award):
                    continue
                if (("director" in award or "cecil" in award or "act" in award) and (not checkIfPerson(h))):
                    continue
                if award in winners:
                    if h.text.lower() in winners[award]:
                        winners[award][h.text.lower()] += 1
                    else:
                        winners[award][h.text.lower()] = 1
                else:
                    winners[award] = {}
                    winners[award][h.text.lower()] = 1
    return winners

### Updates Presenters Dictionary
def updatePresentersDictionary(doc, tweet, presenters, matches):
    if ("present" in tweet or "announc" in tweet or "award" in tweet or "give" in tweet):
        for award in matches:
            pos = [tok.i for tok in doc if ((tok.pos_ == "PROPN" or tok.text.lower() == "will") and not any(i in tok.text.lower().split() for i in tokens_to_ignore))] #maybe include not congrat
            properPronouns = getSolutionsFromPositions(doc, pos)
            for h in (properPronouns):
                if not checkIfPerson(h):
                    continue
                if any(i in h.text.lower() for i in potential_people_answers_to_ignore):
                    continue
                if (h.text.lower() in award):
                    continue
                if award in presenters:
                    if h.text.lower() in presenters[award]:
                        presenters[award][h.text.lower()] += 1
                    else:
                        presenters[award][h.text.lower()] = 1
                else:
                    presenters[award] = {}
                    presenters[award][h.text.lower()] = 1
    return presenters
    
### Updates the Final Answer Dictionary
def updateAnswerDictionary(j, hosts, awardNames, winners, presenters, answer):
    #Hosts
    host_list = sorted(hosts.keys(), key=hosts.get, reverse=True)
    if (hosts != {}):
        p = np.percentile(list(hosts.values()),90)
        ans = []
        for key in host_list:
            if (hosts[key] > p):
                ans.append(key)
        if (len(ans) >= 2):
            answer[j]["hosts"] = ans[:2]
        else:
            myList = []
            myList.append(ans[0])
            answer[j]["hosts"] = myList

    #Awards
    #Find the top 1-2 Names, those will be the people mentioned the most with the word best
    award_list = sorted(awardNames.keys(), key=awardNames.get, reverse = True)
    ans = []
    for i in award_list:
        ans.append(i)
    answer[j]["awards"] = ans[:27]

    #Winners
    winners.pop('golden globe hosts', None)
    for y in winners:
        answer[j]["award_data"][y]["winner"] = max(winners[y], key=winners[y].get)

    presenters.pop('golden globe hosts', None)
    
    for award in awards:
        for x in presenters[award]:
            if answer[j]["award_data"][award]["winner"] in x:
                presenters[award][x] = 0
    for y in presenters:      
        presenters_list = sorted(presenters[y].keys(), key=presenters[y].get, reverse=True)
        if (presenters[y] != {}):
            p = np.percentile(list(presenters[y].values()),1)
            ans = []
            for key in presenters_list:
                if (presenters[y][key] > p):
                    ans.append(key)
            if (len(ans) >= 2):
                answer[j]["award_data"][y]["presenters"] = ans[:2]
            else:
                if ans == []:
                    myList = []
                    myList.append(presenters_list[0])
                    answer[j]["award_data"][y]["presenters"] = myList
                else:
                    myList = []
                    myList.append(ans[0])
                    answer[j]["award_data"][y]["presenters"] = myList
        
    return answer
    
### Checks if the first word in a potential answer is a common name to determine if it is a person
def checkIfPerson(h):
    isPerson = False
    if ((len(h.text.split()) != 2) and (len(h.text.split()) != 3)):
        return False
    for ent in h.ents:
        if ent.label_ == "PERSON" or h.text.lower().split()[0] in names:
            isPerson = True
    return isPerson


### Make Human Readable File ###
def humanReadable(answer):
    string = ""
    for year in answer:
        string += "Year: " + str(year) + "\n"
        string += "Hosts: "
        for i in answer[year]["hosts"]:
            string += i + ", "
        string = string[:-2]
        string += "\nAwards:" + "\n"
        for award in answer[year]["awards"]:
            string += award + "\n"
        string += "\n"
        for award in answer[year]["award_data"]:
            string += "Award: " + award
            string += "\n" + "Presenters: "
            for i in answer[year]["award_data"][award]["presenters"]:
                string += i + ", "
            string = string[:-2]
            string += "\nNominees: "
            for i in answer[year]["award_data"][award]["nominees"]:
                string += i + ", "
            string = string[:-2]
            string += "\nWinner: "
            string += answer[year]["award_data"][award]["winner"]
            string += "\n\n"
        string += "\n"

    f = open("HumanReadableAnswers.txt", "w")
    f.write(string)
    f.close()



### Required Functions ###

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    json_file = open("answers.json")
    answer = json.load(json_file)
    json_file.close()
    hosts = answer[str(year)]["hosts"]
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    json_file = open("answers.json")
    answer = json.load(json_file)
    json_file.close()
    awards = answer[str(year)]["awards"]
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    json_file = open("answers.json")
    answer = json.load(json_file)
    json_file.close()
    nominees = {}
    for i in awards:
        nominees[i] = answer[str(year)]["award_data"][i]["nominees"]
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    json_file = open("answers.json")
    answer = json.load(json_file)
    json_file.close()
    winners = {}
    for i in awards:
        winners[i] = answer[str(year)]["award_data"][i]["winner"]
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    json_file = open("answers.json")
    answer = json.load(json_file)
    json_file.close()
    presenters = {}
    for i in awards:
        presenters[i] = answer[str(year)]["award_data"][i]["presenters"]
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    print("Pre-ceremony starting")
    ## Set Up JSON
    global answer
    global years
    global names
    for year in years:
        answer[year] = {}
        answer[year]["hosts"] = []
        answer[year]["awards"] = {}
        answer[year]["award_data"] = {}
        for i in awards:
            answer[year]["award_data"][i] = {"nominees": [], "presenters": [], "winner":""}

        ## Make Dictionaries for hosts, nominees, presenters, and winners
        hosts = {}
        awardNames = {}
        winners = {}
        presenters = {}

        ## Cycle Through Tweets
        tweets = pd.read_json("gg" + str(year) + ".json")
        for x, col in tweets.iterrows():
            tweet = col["text"]
            if "RT" in tweet: #Prevents getting the same tweet multiple times
                continue
            #This if statement is so tweets that dont fit any of these are not looked at at all
            #if ("host" in tweet.lower()) or ("best " in tweet.lower()) or (("won" in tweet.lower() or "congrat" in tweet.lower() or "winner" in tweet.lower() or "goes to" in tweet.lower()) and ("best" in tweet.lower() or "cecil" in tweet.lower())) or (("present" in tweet.lower() or "announc" in tweet.lower() or "give" in tweet.lower() or "award" in tweet.lower()) and ("best" in tweet.lower() or "cecil" in tweet.lower())): 
            matches = checkKeyWords(key_word_award_mapping, tweet.lower())
            if matches != []:
                #if 'golden globe hosts' in matches:
                #if ((("won" in tweet.lower() or "congrat" in tweet.lower() or "winner" in tweet.lower() or "goes to" in tweet.lower()) and ("best" in tweet.lower() or "cecil" in tweet.lower())) or ("present" in tweet or "announc" in tweet or "award" in tweet or "give" in tweet)):                    
                doc = nlp(tweet)
               #     print(tweet)
               # else:
               #     continue
            else:
                continue
                
            tweet = tweet.lower()
            ##Check if Host
            hosts = updateHostDictionary(doc, tweet, hosts)
            #Check if Award Name
            awardNames = updateAwardNamesDictionary(doc, tweet, awardNames)
            #Check if Award Winner
            winners = updateWinnersDictionary(doc, tweet, winners, matches)
            #Check for Presenters
            presenters = updatePresentersDictionary(doc, tweet, presenters, matches)
        #Fill in final JSON
        answer = updateAnswerDictionary(year, hosts, awardNames, winners, presenters, answer)
    print("Pre-ceremony processing complete.")
    with open("answers.json", "w") as outfile:
        json.dump(answer, outfile)
    humanReadable(answer)
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    global answer
    answer = {}
    global years
    years = [2015]
    global names
    with open('names.txt',"r") as f:
        names = f.read()
    names = names.lower().split("\n")
    answer = pre_ceremony()   
    return
if __name__ == '__main__':
    main()