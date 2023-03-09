import requests
from secrets import GITHUB_TOKEN
#from pprint import pprint


def get_github_issue_metadata(repo,issue_num):
    """
    This function get id for given issue number.
    """

    headers = {"Authorization":f"token {GITHUB_TOKEN}",
               "Accept":"application/vnd.github.v3+json"}
    params = {"state": "all",
              "filter": "all"}


    issue_url = f"https://api.github.com/repos/Kaiasm/{repo}/issues/{issue_num}"
    r = requests.get(issue_url, headers=headers,params=params).json()
    return r


#pprint(get_github_issue_metadata("coherence", 2181))

