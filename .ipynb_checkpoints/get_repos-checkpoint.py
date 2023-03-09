import requests

url = "https://api.github.com/users/Kaiasm/repos"
headers = {"Accept": "application/vnd.github.interia-preview+json"}
my_token = "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"
username = "Mariusz-kaiasm"
r = requests.get(url, headers=headers, auth=(username, my_token))
print(type(r))

