from requests import exceptions, request
from secrets import GITHUB_TOKEN

# This is someone else work 
class GitHubQuery:
    BASE_URL = "https://api.github.com/graphql"
    ORGANIZATION = "Kaiasm"

    def __init__(
        self,
        github_token=GITHUB_TOKEN,
        query=None,
        query_params={"state": "all",
              "filter": "all",
              "per_page": 100,
              "page":5},
        additional_headers={"Accept":"application/vnd.github.v3+json"}
    ):
        self.github_token = github_token
        self.query = query
        self.query_params = query_params
        self.additional_headers = additional_headers or dict()

    @property
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )
        return {
            **default_headers,
            **self.additional_headers
        }

    def generator(self):
        while(True):
            try:
                yield request(
                    'post',
                    GitHubQuery.BASE_URL,
                    headers=self.headers,
                    json=dict(query=self.query.format_map(self.query_params))
                ).json()
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    def iterator(self):
        pass

