import requests
from secrets import GITHUB_TOKEN
from pprint import pprint


def get_rep_issues():

    org_url = "https://api.github.com/search/repositories?q=org:Kaiasm"
    headers = {"Authorization":f"token {GITHUB_TOKEN}",
               "Accept":"application/vnd.github.v3+json"}
               
    params = {"state": "all",
              "filter": "all",
              "per_page": 50}

    resp_dict = requests.get(org_url, headers=headers, params=params).json()
    
    repos_list = []
    repo_issues_dict = dict()

    print("Paginating repos for issue numbers ....")

    for repo in resp_dict["items"]:
        repos_list.append(repo["name"])

    for i in range(len(repos_list)):
        nextPage = True
        page = 1
        total_results = []
        while nextPage:
        
            issue_url = f"https://api.github.com/repos/Kaiasm/{repos_list[i]}/issues?search=a&page={page}"
            # Grab the search results
            response = requests.get(issue_url, headers=headers, params=params)
            
            data = response.json()
        
            if data == []:
                nextPage = False
            else:
                total_results.extend(data)
                page += 1
       
        issue_list = []

        for issue in total_results:   
            issue_list.append(issue["number"]) 
        
        repo_issues_dict[repos_list[i]] = issue_list

    return repos_list, repo_issues_dict


