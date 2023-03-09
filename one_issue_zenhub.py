import requests
from secrets import ZENHUB_TOKEN
#from pprint import pprint



def get_zenhub_issue_metadata(repo_id, issue_num):

    """Return metadata for given issue numer from ZenHub"""

    base_url = "https://api.zenhub.com/"
    headers = {"X-Authentication-Token": ZENHUB_TOKEN}

    issue_url = base_url + f"p1/repositories/{repo_id}/issues/{issue_num}" 

    issue_response = requests.get(issue_url, headers=headers).json()

    return issue_response


#pprint(get_zenhub_issue_metadata(88064037, 2161))
