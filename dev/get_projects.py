import requests
from secrets import GITHUB_TOKEN
import json


if __name__ == "__main__":


    projects_url = "https://api.github.com/orgs/Kaiasm/projects"

    headers = {"Authorization":f"token {GITHUB_TOKEN}",
               "Accept":"application/vnd.github.v3+json"}

    params = {"state": "all"}

    project_response = json.loads(requests.get(projects_url, headers=headers, params=params).text)
    print(json.dumps(project_response, indent=4, sort_keys=True))

    repo_project_url = "https://api.github.com/repos/Kaiasm/treecreeper/projects"

    #repo_project_resp = json.loads(requests.get(repo_project_url, headers=headers, params=params).text)
    #print(json.dumps(repo_project_resp, indent=4, sort_keys=True))



