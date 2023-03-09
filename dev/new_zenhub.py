from matplotlib.pyplot import get
import requests
from secrets import ZENHUB_TOKEN
#from pprint import pprint

def get_repos_ids():

    base_url = "https://api.zenhub.com/"
    headers = {"X-Authentication-Token": ZENHUB_TOKEN}

    # Get ZenHub Workspaces for a repository
    workspace_url = base_url + "p2/repositories/84338281/workspaces"  # treecreeper repo number
    response = requests.get(workspace_url, headers=headers)

    boards = response.json()

    for i in range(len(boards)):
        print(f"{boards[i]['name'].capitalize()} number of repos= {len(boards[i]['repositories'])}")  

    return boards




#pprint(get_repos_ids())