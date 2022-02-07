import requests
import json
import time

# Modify BASE_URL accordingly
BASE_URL = "https://finance.yahoo.com/screener/unsaved/79fce2f7-82fe-49ec-8098-88add84138ec?dependentField=sector&dependentValues=&offset=OFFSET&count=COUNT"

cnt = 100
offset = 0
flag = 1
temp  = 10
name_to_symbol = []
total = 0

while flag > 0:
    url = BASE_URL.replace("OFFSET", str(offset))
    url = url.replace("COUNT",str(cnt))
    offset += cnt
    
    response = requests.get(url, headers={'User-Agent': 'Custom'})
    s = str(response.text)
    jsonArrayStart = s.find('"results":{"rows"') + 18
    jsonArrayEnd = jsonArrayStart + 1

    while s[jsonArrayEnd] != ']':
        jsonArrayEnd += 1
    
    jsonArrayString = s[jsonArrayStart: jsonArrayEnd+1]
    jsonArray = json.loads(jsonArrayString)
    if len(jsonArray) != cnt:
        flag = 0
    
    total += len(jsonArray)
    for obj in jsonArray:
        if 'longName' in obj:
            name_to_symbol.append([obj['symbol'], obj['longName']])
        elif 'shortName' in obj:
            name_to_symbol.append([obj['symbol'], obj['shortName']])
        else:
            name_to_symbol.append([obj['symbol'], obj['symbol']])
    time.sleep(10)
    
print(name_to_symbol)