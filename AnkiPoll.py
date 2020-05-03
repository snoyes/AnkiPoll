import json
import urllib.request
from bs4 import BeautifulSoup
import re
import logging

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    try:
        requestJson = json.dumps(request(action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    except urllib.error.URLError as ex:
        print("Could not reach Anki. Is Anki running and the AnkiConnect add-on installed?")

def parseCollectionStats(stats_html):
    soup = BeautifulSoup(stats_html, features="html.parser")
    section = soup.find("h1", text="Today").parent
    m = re.search(r"Studied \u2068(?P<numcards>\d*)\u2069 cards.*in \u2068(?P<duration>\d*(\.\d*)?)\u2069 (?P<timeunits>.*)\u2069 today", str(section), re.DOTALL)
    if m:
        return m.groupdict()
    elif str(section).find("No cards have been studied today"):
        return {'numcards': '0', 'duration': '0', 'timeunits': 'seconds'}
    else:
        logging.error("Failure parsing the collection stats.", section)
        return {'numcards': '0', 'duration': '0', 'timeunits': 'seconds'}
    
if __name__ == "__main__":

    for name in invoke('getProfiles'):
        invoke('loadProfile', name=name)
        # Anki may be set to auto sync when switching profiles. If not, invoke('sync')
        due = invoke('findCards', query='is:due')
        new = invoke('findCards', query='is:new')
        studied = invoke('findCards', query='rated:1')
        stats_html = invoke('getCollectionStatsHTML')
        stats = parseCollectionStats(stats_html)

        print('{name} has {due} due, {new} new, studied {numcards} cards ({distinctcards} distinct) for {duration} {timeunits} today'.format(
            name=name,
            due=len(due),
            new=len(new),
            distinctcards=len(studied),
            numcards=stats['numcards'],
            duration=stats['duration'],
            timeunits=stats['timeunits']
            )
        )

    #invoke('guiExitAnki')
