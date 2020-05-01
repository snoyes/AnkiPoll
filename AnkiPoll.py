import json
import urllib.request

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
    

def countStudied(name):
    switchProfile(name)
    studied = invoke('findCards', query='rated:1')
    return len(studied)

def switchProfile(name):
    invoke('loadProfile', name=name)

if __name__ == "__main__":

    for name in invoke('getProfiles'):
        switchProfile(name)
        # Anki may be set to auto sync when switching profiles. If not, invoke('sync')
        due = invoke('findCards', query='is:due')
        new = invoke('findCards', query='is:new')
        studied = invoke('findCards', query='rated:1')

        print('{name} has {due} due, {new} new, studied {studied} today'.format(
            name=name,
            due=len(due),
            new=len(new),
            studied=len(studied)
            )
        )

    #invoke('guiExitAnki')
