import requests
import json
import sys
from datetime import datetime, timedelta

until_dt = datetime.now()
since_dt = until_dt - timedelta(hours = 24)
commits_params = {
    "since" : since_dt.strftime("%Y-%m-%dT%H:%M:%S"),
    "until" : until_dt.strftime("%Y-%m-%dT%H:%M:%S")
}
response = requests.get("https://api.github.com/repos/facebook/react/commits", params=commits_params)
if response.status_code == 200:
    commits = response.json()
    if len(commits) < 2:
        print("There has been less than 2 commits in the last 24 hours")
else:
    print("Error while requesting commits of the day")

response = requests.get("https://api.github.com/repos/facebook/react/contributors?page=1&per_page=100", params={"anon":"True"})
contrib_json = response.json()
all_contrib = [contrib_json]
i = 2
while response.status_code == 200 and len(contrib_json) == 100:
    response = requests.get("https://api.github.com/repos/facebook/react/contributors?page=" + str(i) +"&per_page=100", params={"anon":"True"})
    contrib_json = response.json()
    if contrib_json:
        all_contrib.append(contrib_json)
    i += 1
if response.status_code != 200:
    print("Error while requesting contributors")
    sys.exit()

commits = 0
contributors = []
anonymous = 0
i = 1
for contrib in all_contrib:
    for user in contrib:
        commits += int(user["contributions"])
        if user["type"] == "User":
            contributors.append([user["login"], user["contributions"]])
        else:
            contributors.append(["anon-" + str(i), user["contributions"]])
            anonymous += int(user["contributions"])
            i += 1
contributors.append(["TOTAL" , commits])

# calcul de la proportion des contributeurs qui ont réalisé le même nombre de contributions a chaque ligne
len = len(contributors) - 1
i = 1
def count_equals(contributors, value):
    count = 0
    for user in contributors:
        if value == user[1]:
            count += 1
    return count

for user in contributors[:-1]:
    proportion = (count_equals(contributors, user[1]) / len) * 100
    user.append(round(proportion, 2))
    i += 1

with open(until_dt.strftime("react_contrib_%Y-%m-%d")+'.json', 'w', encoding='utf-8') as f:
    json.dump(contributors, f, ensure_ascii=False, indent=4)