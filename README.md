# ZenHub Migration to GitHub Projects Beta

In the past Kaiasm was utilizing Zenhub as an “Issue Management Overlay” for Github. Now, we are looking to use Github projects, and we needed to “translate” the metadata we have used with Zenhub to the appropriate metadata we need in Github projects. In this project I reproduce the current Zenhub pipelines with GitHub projects by using GitHub API and GraphQL querries. Prior to full implementation, as stated in the documentation, needs to be performed on the repo’s in (reverse) size and importance order.

## get_repos2.py
Paginating through GitHub repos and
returns a dictionary with repos and their issues.

## one_issue_github.py
- takes in a repo name as it appears in GitHub as first argument,
- takes in an issue num as second argument,

Returns a GitHub metadata for given issue.

## on_issue_zenhub.py
- takes in a repo id as it appears in ZenHub as first argument,
- takes in an issue num as second argument,

Returns a ZenHub metadata for given issue.

## get_project.py, new_attempt.py in Dev folder
These scripts are my attempts for the projects but
they haven't been used.

## new_zenhub.py in Dev folder
Returns a dictionary with boards names and
their repos ids from ZenHub.

## secrets.py
Contains tokens for ZenHub and GitHub

## main.py
This is my main script contains functions needed to
mutate issues to project beta and update them to the correct
pipeline as it was in ZenHub. This file contains multiple functions
which uses GitHub api to collect needed information from
github repos. There are also few functions which are using
graphql queries as this is the only way to mutate and update
projects beta in GitHub.

## beta_project_ids.json in generated folder
Contains the names and projects beta Ids 
collected by using graphQL query.

## full_repos_issues.json in generated folder
Contains names of all repos and numbers of issues 
collected by get_repos2.py from GitHub.

## repos_issues.json in generated folder
Contains repos names and their issues from GitHub. 
Coherence and production repos has been
reduced by removing closed ones as these
repos were to big to mutate them into 
relevant project beta (there is a cap of 1200 cards
in a project beta)

## zenhub_metadata subfolder 
Contains json file with all metadata we can collect from ZenHub for all repos and their issues.




# How to run this script

Simple run main.py to check if any new issues has been created. Ones the script is finished, all issues which haven't been assigned to correct project beta will be placed in "no status" pipeline. If someone who created an issue will assign it to the project beta but will not point it to the right pipeline, the issue will still appear in "no status" pipeline.

The main.py script has also other features like updating project beta pipelines in the way how they've been shown in Zenhub or a feature to delete all issues from a project beta. Some of these features are #commented or set up as False. For example I set update_pipes argument to False in "run_main" function as we no longer need it. If we do it now it'll destroy all the work everyone has done so far and it would update pipelines according to what was in Zenhub since we've stopped usinig it.

### Run time

We can limit time of running the script by setting default values in "create_json_files" function to False as long as we are sure that our json file is up to date. I've also limited number of new issues to 20 per repo spo it will not mutate issues which are already there, but if you suspect that the number of new issues is greater than 20 simple change the value in "run_mutation"  function.



