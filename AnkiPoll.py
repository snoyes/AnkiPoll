import json
import urllib.request

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
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

def countStudied(name):
    switchProfile(name)
    studied = invoke('findCards', query='rated:1')
    return len(studied)

def switchProfile(name):
    invoke('loadProfile', name=name)

if __name__ == "__main__":
    with open('ankiProfileNames.txt', 'r') as f:
        names = f.read().splitlines()

    for name in names:
        switchProfile(name)
        # Anki is set to auto sync. If you don't want that, invoke('sync')
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
