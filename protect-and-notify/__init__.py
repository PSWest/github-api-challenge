import logging
import azure.functions as func
import os
import requests
import json

username = os.environ["User"]
token = os.environ["GitHubToken"]
org = os.environ["OrgName"]
branch = os.environ["BranchName"]


def get_api_request(url, params=None):
    session = requests.Session()
    session.auth = (username, token)
    headers = {'Accept': 'application/vnd.github.v3+json'}
    request = session.get(url=url, headers=headers, params=params)
    if hasattr(request, 'links') and 'next' in request.links.keys():
        link = request.links['next']['url']
    request = request.json()
    response = list()
    response.append(request)
    if 'link' in locals():
        next_request = requests.get(url=link, params=params)
        next_request = next_request.json()
        response.append(next_request)
        while hasattr(next_request, 'links') and 'next' in request.links.keys():
            next_link = next_request.links['next']['url']
            next_request = session.get(url=next_link, params=params)
            next_request = next_request.json()
            response.append(next_request)
    print(f'Successful Request To: {url}')
    return response


def post_api_request(url, data):
    session = requests.Session()
    session.auth = (username, token)
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = session.post(url=url, data=data, headers=headers)
    response = response.json()
    print(f'Successfully Posted To: {url}')
    return response


def put_api_request(url, data):
    session = requests.Session()
    session.auth = (username, token)
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = session.put(url=url, data=data, headers=headers)
    response = response.json()
    print(f'Successfully Put To: {url}')
    return response


# Get Repo main Branch


def get_unprotected_branches(repo_path):
    url = f'https://api.github.com/repos/{repo_path}/branches'
    params = {'protected': 'false', 'per_page': 100}
    branches = get_api_request(url, params)
    branch_status = dict()
    for branch_json in branches:
        branches = branch_json
        for unprotected_branch in branches:
            if 'main' in unprotected_branch['name']:
                unprotected_branch = {repo_path: unprotected_branch['protected']}
                branch_status.update(unprotected_branch)
            else:
                print(f'Repo: "{repo_path}", Returned No Unprotected Branches')
    return branch_status


def get_branch_protection(repo_path):
    url = f'https://api.github.com/repos/{repo_path}/branches/{branch}/protection'
    protection = get_api_request(url)
    return protection

# Set Branch Protection


def set_branch_protection(repo_path):
    url = f'https://api.github.com/repos/{repo_path}/branches/{branch}/protection'
    data = {
        'checks': [{
            "context": "context"
        }],
        'strict': False,
        'contexts': None,
        'restrictions': None,
        'enforce_admins': False,
        'allow_deletions': False,
        'allow_force_pushes': True,
        'required_status_checks': None,
        'required_linear_history': True,
        'required_pull_request_reviews': {
            "require_code_owner_reviews": True,
            "required_approving_review_count": 2
        },
        'required_approving_review_count': 2,
        'required_conversation_resolution': True
    }
    protection = put_api_request(url, json.dumps(data))
    print(f'Branch: "{repo_path}/{branch}" Has Been Protected')
    return protection

# Create Repo Issue


def create_repo_issue(repo_path):
    url = f'https://api.github.com/repos/{repo_path}/issues'
    title = f'ALERT: Protection Enabled For Branch: "{repo_path}/{branch}"'
    labels = ["Notification", "Protected"]
    body = f'A New Repo: "{repo_path}", Has Been Created And Branch Protection Has Been Enabled For Branch: "{branch}"'
    data = {
        'title': title,
        'body': body,
        'labels': labels
    }
    issue = post_api_request(url, json.dumps(data))
    print(
        f'Issue {issue["number"]} Created For Branch: "{repo_path}/{branch}"')
    return json.dumps(issue['number'])


def create_repo_issue_comment(repo_path, issue_number):
    url = f'https://api.github.com/repos/{repo_path}/issues/{issue_number}/comments'
    protection = get_branch_protection(repo_path)
    body = f'@afretwell,\n Branch: "{repo_path}/{branch}", has been protected with the following settings: \n {json.dumps(protection, indent=4)}'
    data = {'body': body}
    request = post_api_request(url, json.dumps(data))
    return request

# Checks for org repo create events, checks for unprotected branches, applies protection, then notifies


def check_and_set_branch_protection(repo_path):
    branch_list = dict()
    success_message = list()
    unprotected_branches = get_unprotected_branches(repo_path)
    branch_list.update(unprotected_branches)
    if branch_list:
        for repo_name in branch_list:
            set_branch_protection(repo_name)
            issue_number = create_repo_issue(repo_name)
            create_repo_issue_comment(repo_name, issue_number)
            message = f'Successfully Set Branch Protection For "{repo_name}/{branch}" And Notified Admin.'
            success_message.append(message)
    else:
        success_message = "Found No Unprotected Branches"    
    return f'{success_message}'


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass

    if req_body['action'] == 'created':
        repo_path = req_body['repository']['full_name']
        response = check_and_set_branch_protection(repo_path)
        logging.info(response)
    return func.HttpResponse(
        body=response,
        status_code=200
    )
