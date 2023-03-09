import requests
import json
import time
from pprint import pprint
# import pandas as pd
from one_issue_github import get_github_issue_metadata
from one_issue_zenhub import get_zenhub_issue_metadata
from get_repos2 import get_rep_issues
from secrets import GITHUB_TOKEN

def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
      return request.json()
    else:
        raise Exception('Query failed to run by returning code of {0}. {1}'.format(request.status_code, query))



def json_extract(obj, key):
  """Recursively fetch values from nested JSON"""
  arr = []
  def extract(obj, arr, key):
    if isinstance(obj, dict):
      for k, v in obj.items():
        if isinstance(v, (dict, list)):
          extract(v, arr, key)
        elif k == key:
          arr.append(v)

    elif isinstance(obj, list):
      for item in obj:
        extract(item, arr, key)
    return arr

  values = extract(obj, arr, key)
  return values



def get_project_beta_ids():
  """
  Returns project beta repos
  with id
  """

  query_projects = """{
  organization(login: "Kaiasm") {
    projectsNext(first: 30) {
      nodes {
        id
        title
        number
        }
      }
    }
  }"""

  result = run_query(query_projects)
  id = json_extract(result, "id")
  title = json_extract(result, "title")
  d = dict(zip(title, id))

  key_to_remove = ['BreadKnife_removed', 'Daddy_removed', 'DataSource_removed',
         'IT Support_removed', 'TestSystem_removed', 'Www_removed']
  for key in key_to_remove:
    if key in d.keys():
      d.pop(key)
    else:
      continue
  return d
 


def mutate_issues_to_beta(project_id, content_id, num):
  """ This Function mutate an issue 
      to the GitHub project beta
      and update to the right pipeline
  """
  query_mutation = """
  mutation {
    addProjectNextItem(input: {projectId: "%s" contentId: "%s"}) {
      projectNextItem {
        id
      }
    }
  }
  """
  query_mutation = query_mutation % (project_id,content_id)
  return run_query(query_mutation)



def run_mutation(repos_issues, repo_name, beta_id, beta_repo):

  print(f"Mutating issues to GitHub project beta repo {beta_repo} ....")
  # will update only 20 or less first issues
  if len(repos_issues[repo_name]) > 20:  # change this value if you haven't run the script for a while
    repos_issues[repo_name] = repos_issues[repo_name][:20]  # change this value as well
  else:
    repos_issues[repo_name] = repos_issues[repo_name]

  for num in repos_issues[repo_name]:
    github_issue_req = get_github_issue_metadata(repo_name, num)
    github_issue_nodes_id = json_extract(github_issue_req, "node_id")[0]

    mutate_issues_to_beta(beta_id, github_issue_nodes_id, num)



def get_value_name(id):
  """
  Query ZenHub project beta card.
  Returns a dictionary with name and id
  of all pipelines.
  """
  query_projects_cards = """
  query{
    node(id: "%s") {
      ... on ProjectNext {
        fields(first: 20) {
        nodes {
          id
          name
          settings
          }
        }
      }
    }
  }
  """


  query_update = query_projects_cards % (id)
  result = run_query(query_update)
  cards_id = json_extract(result, "id")[2]
  settings_extract_dict = json.loads(json_extract(result, "settings")[2])
  value_id = json_extract(settings_extract_dict, "id")
  name = json_extract(settings_extract_dict, "name")

  d = dict(zip(name, value_id))
  return d, cards_id



def get_project_items(id):
  query_project_items = """{
    node(id: "%s") {
    ... on ProjectNext {
      items(first: 1) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          endCursor
        }
        nodes {
          title
          id
          fieldValues(first: 8) {
            nodes {
              value
              projectField {
                name
                id
              }
            }
          }
          content {
            ... on Issue {
              number
              labels(first: 3) {
                nodes {
                  name
                  }
                }
              }
            }
          }
        }
      }
    }
  }"""

  query_update = query_project_items % (id)
  result = run_query(query_update)
  return result



def get_project_items2(id, cursor):
  query_project_items = """{
    node(id: "%s") {
    ... on ProjectNext {
      items(first: 1 after: "%s") {
          pageInfo {
          hasNextPage
          hasPreviousPage
          endCursor
        }
        nodes {
          title
          id
          fieldValues(first: 8) {
            nodes {
              value
              projectField {
                name
                id
              }
            }
          }                                         
          content {
            ... on Issue {
              number
              labels(first: 3) {
                nodes {
                  name
                  }
                }
              }
            }
          }
        }
      }
    }
  }"""

  query_update = query_project_items % (id, cursor)
  result = run_query(query_update)
  return result



def get_field_value(num_list, names_list, values_list, ids_list, srch_value):
    """
    Functions gets list of list names and values,
    search for index of name of the field we want to 
    look for. Retruns a list of tuples with number,
    name and value.
    """
    l = []
    for i, num in enumerate(num_list):
      if srch_value in names_list[i]:
        idx = names_list[i].index(srch_value)
      else:
        idx = -1
      name = names_list[i][idx]
      value = values_list[i][idx]
      ids = ids_list[i][-1]
      l.append((num, name, value, ids))
    return l



def get_issues_beta_ids(repo_id):
  """
  This function paginate repo pages.
  Returns dictionary with key as title
  and value as id_node from Github 
  project beta.
  
  """
  print("Collecting metadata from project beta ...")
  beta_ids = []
  beta_names = []
  beta_values = []
  beta_num = []
  items_id = get_project_items(repo_id)
  #pprint(items_id)
  has_next_page = json_extract(items_id, "hasNextPage")[0]
  end_cursor = json_extract(items_id, "endCursor")[0]
  beta_title = json_extract(items_id, "title")
  beta_ids.append(json_extract(items_id, "id"))
  beta_num.append(json_extract(items_id, "number"))
  beta_names.append(json_extract(items_id, "name"))
  beta_values.append(json_extract(items_id, "value"))
  while has_next_page:
    next_page = get_project_items2(repo_id, end_cursor)
    #pprint(next_page)
    beta_title.extend(json_extract(next_page, "title"))
    beta_ids.append((json_extract(next_page, "id")))
    beta_names.append(json_extract(next_page, "name"))
    beta_values.append(json_extract(next_page, "value"))
    beta_num.append(json_extract(next_page, "number"))
    has_next_page = json_extract(next_page, "hasNextPage")[0]
    end_cursor = json_extract(next_page, "endCursor")[0]
    
    if end_cursor == None:
      end_cursor = False
  beta_num = [x[0] for x in beta_num]
  field_values = get_field_value(beta_num, beta_names,
                                 beta_values, beta_ids, "Estimate")

  #pprint(field_values)


  isuses_beta_pipe_dict = dict(zip(beta_title,[x[0] for x in beta_ids]))

  #pprint(isuses_beta_pipe_dict)


  return isuses_beta_pipe_dict ,beta_num, field_values



def update_project_beta_pipes(repos_issues, github_repo_name, 
                              zenhub_id, beta_repo, beta_repo_id): 
  """
  Collects metadata for given issue number from Zenhub and Github,
  updates Github project and its pipelines.

  """
  
# Query for moving an issue to the pipeline
  query_project_item_update = """                         

  mutation {
    updateProjectNextItemField(
      input: {
        projectId: "%s"   
        itemId: "%s" 
        fieldId: "%s"
        value: "%s"
        number: "%s"
      }
    ) {
      projectNextItem {
        id
      }
    }
  }
  """

  project_beta_dict, field_id = get_value_name(beta_repo_id)
  beta_issues_ids_dict,_ = get_issues_beta_ids(beta_repo_id)

  #pprint(beta_issues_ids_dict)

  print(f"Collecting metadata for {beta_repo} from Zenhub ...")

  key1 = "pipeline"
  key2 = "pipelines"
  title_value_ids = dict()
  title_num_issues = dict()

  for num in repos_issues[github_repo_name]:
    print(f"Issue number: {num}")
    
    zenhub_issue_name = get_zenhub_issue_metadata(zenhub_id, num)
    github_issue = get_github_issue_metadata(github_repo_name, num)
    github_issue_state = json_extract(github_issue, "state")
    github_issue_title = json_extract(github_issue, "title")[0]
    title_num_issues[github_issue_title] = num

    
    if github_issue_state[0].lower() == "closed":
      name = "Closed"
      value_id = project_beta_dict[name]
      title_value_ids[github_issue_title] = value_id

    elif key1 in zenhub_issue_name.keys():
      name = zenhub_issue_name["pipeline"]["name"]
      value_id = project_beta_dict[name]
      title_value_ids[github_issue_title] = value_id

    elif key2 in zenhub_issue_name.keys():
      name = zenhub_issue_name["pipelines"][0]["name"]
      value_id = project_beta_dict[name]

      title_value_ids[github_issue_title] = value_id
      

  print(f"Updating issues for {beta_repo} in project beta ....")
  for title, value_id in title_value_ids.items():
    if title in beta_issues_ids_dict.keys():
      item_id = beta_issues_ids_dict[title]
      number = title_num_issues[title]
      query_update = query_project_item_update % (beta_repo_id, item_id, field_id, 
                                                  value_id, number)
      run_query(query_update)
    else:
      continue
  print(f" Updating {beta_repo} finished successfully!")



def create_json_files(github, beta, full_run= True, create_files=True):
  """
  This function collects all issues for relevant GitHub repo
  and save it in json file.
  """
  if full_run:
    _, repos_issues = get_rep_issues()
    with open("generated/full_repos_issues.json", "w") as f:
      json.dump(repos_issues, f)
  while create_files:
    with open("generated/full_repos_issues.json", "r") as json_file:
      repos_issues = json.load(json_file)

    huge_repos = ["coherence", "production"]

    for name in huge_repos:
      print(f"Removing closed issues from {name} ...")
      count = 0
      new_list = []
      for num in repos_issues[name]:
        github_issue = get_github_issue_metadata(name, num)
        state = json_extract(github_issue, "state")

        if state[0].lower() != "closed" :
          new_list.append(num)
          count += 1
      print(f"Open issues in {name}= {count}")
      repos_issues[name] = new_list
  
    for key in github:
      if key in repos_issues:
        del repos_issues[key]

    with open('generated/repos_issues.json', 'w') as f:
      json.dump(repos_issues, f)

    beta_projects_id_dict = get_project_beta_ids()
    for key in beta:
      if key in beta_projects_id_dict.keys():
        del beta_projects_id_dict[key]

    with open('generated/beta_projects_ids.json', 'w') as f:
      json.dump(beta_projects_id_dict, f)

    create_files = False



def project_item_delete(repo_name, project_beta):
  query_project_item_delete = """
    mutation {
      deleteProjectNextItem(
        input: {
          projectId: "%s"
          itemId: "%s"
        }
      ) {
        deletedItemId
    }
  }
  """
  project_id = project_beta[repo_name]
  beta_issues, _ = get_issues_beta_ids(project_id)
  print(f"Project beta: {repo_name}")
  for issue_id in beta_issues.values():
    print(issue_id)
    query_update = query_project_item_delete % (project_id, issue_id)
    run_query(query_update)



def run_main(update_pipes):
  # Main loop for mutating
  for gitkey in repos_issues.keys():
    for betakey in beta_projects_id_dict.keys():
      if gitkey.lower() == betakey.lower():
        run_mutation(repos_issues, gitkey,
                      beta_projects_id_dict[betakey], betakey)
        if update_pipes:
          update_project_beta_pipes(repos_issues, gitkey, zenhub_dict[gitkey],
                              betakey, beta_projects_id_dict[betakey])



def zenhub_metadata():
    """
    Function collects all metadata from Zenhub
    and dumps it into json file.
    """
    path = "zenhub_metadata\metadata.json"
    temp_dict = dict()
    inner_dict = dict()
    for gitkey in repos_issues.keys():
      for zenkey in zenhub_dict.keys():
        if gitkey.lower() == zenkey.lower():
          count = 0
          for num in repos_issues[gitkey]:
            print(count)
            if count == 30:
              time.sleep(120)
              count = 0 
            zenhub_issue = get_zenhub_issue_metadata(zenhub_dict[zenkey], num)
            pprint(zenhub_issue)
            inner_dict[num] = zenhub_issue
            count += 1
          pprint(inner_dict)
          temp_dict[zenkey] = inner_dict

    with open(path, "w") as jsonfile:
      json.dump(temp_dict, jsonfile)


def print_save_report(repos_issues):
  """
  This function calclulates new issues found from 
  the last run and produce a tabel output and 
  replace last report file.
  """
  new_run = {}
  for k, v in repos_issues.items():
    new_run[k] = len(v)

  with open("report/last_report.json", "r") as f:
    last_report = json.load(f)
  temp = {}
  for k, v in last_report.items():
    temp[k] = new_run[k] - v

  #df = pd.DataFrame.from_dict(temp, orient="index", columns=["new issues found"])
  #print(df)

  pprint(temp)

  with open("report/last_report.json", "w") as f:
      json.dump(new_run, f)


if __name__ == "__main__":
  
  headers = {"Authorization":f"token {GITHUB_TOKEN}"}

  # List of zenhub repos ids ordered as repos_issues.keys()
  zenhub_repos_ids = [392253521, 32987147, 17138397, 88064037, 265858332, 
                      380983338, 91701404, 88168363, 112597289,14806027, 
                      18179919, 260476172, 51430580, 146448336, 18336751, 
                      51430736, 11922093, 337763304, 84338281, 33732425] 


  # Removed repos as they do not contain any issues
  github_repos_removed = ['test-website', 'engine']
  beta_repos_removed = ['Engine'] 

  # Github repos with issues numbers and beta project repos with ids
  create_json_files(github_repos_removed, beta_repos_removed, 
                    full_run=False, create_files=False)
  
  # Load data collected from Github repos and beta projects
  with open('generated/repos_issues.json') as jsonfile:
    repos_issues = json.load(jsonfile)

  with open('generated/beta_projects_ids.json') as jsonfile:
    beta_projects_id_dict = json.load(jsonfile)

  # Extract Onokai beta repo id from dictionary
  onokai_dict = {key:val for key, val in beta_projects_id_dict.items() if key == 'OntoKai'}
  beta_projects_id_dict = {key:val for key, val in beta_projects_id_dict.items() if key != 'OntoKai'}

  # Remove issues from coherence which are in onokai
  _, onokai_num_list, _ = get_issues_beta_ids(onokai_dict["OntoKai"])
  temp_list = []

  beta_ontokai = get_issues_beta_ids(onokai_dict["OntoKai"])

  ontokai_items = get_project_items(onokai_dict["OntoKai"])

  #for num in onokai_num_list:
    #if num in repos_issues["coherence"]:
      #temp_list.append(num)
  # we do not want to remove ontokai issues from coherence
  #repos_issues["coherence"] = [x for x in repos_issues["coherence"] if x not in temp_list]
  
  # Sort repos_issues alphabetically
  repos_issues = dict(sorted(repos_issues.items()))
  github_repos_names = repos_issues.keys()

  # Create dictionary with github repos names and zenhub ids
  zenhub_dict = dict(zip(github_repos_names, zenhub_repos_ids))

  # Print and save the report 
  print_save_report(repos_issues)

  # Main Loop (uncomment it if you want to run it, and change update_pipes to True if you want to update pipes)
  run_main(update_pipes=False)

  # Loop for deleting closed issues from beta project
  #repos_list_to_remove = ["Coherence", "Production"]
  #for repo_name in repos_list_to_remove:
    #project_item_delete(repo_name, beta_projects_id_dict)


  # This function collect metadata from Zenhub and save it in zenhub_metadata folder
  #zenhub_metadata()


