import os
import requests
import json
import re
from tqdm import tqdm
import progressbar


def main():
    with open('parameters.txt') as f:
        data = {}
        for line in f:
            key, value = line.strip().split(':')
            data[key] = value
    f.close()

    scmToken = data['SCM_TOKEN']
    owner = data['REPO_OWNER']
    repo = data['REPO_NAME']
    jiraInstance = data['JIRA_INSTANCE']
    jiraToken = data['JIRA_TOKEN']   

    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/pulls?state=open&per_page=100'

    headers = {
        'Authorization': 'token ' + scmToken
    }

    values = ''
    
    request = requests.request('GET', endpoint, headers=headers, data=values)
    response = request.json()
    
    count = 0
    x = 0

    while count < len(response):        
        if '[Snyk]' in response[count]['title']:
            if 'Jira' not in response[count]['body']:
                pullNumber = response[count]['number']
                # issueUrl = extractUrl(response[count]['body'])
                urlList = extractUrls(response[count]['body'])
                if urlList:
                    urlCount = len(urlList)
                    x = 1
                    while x <= urlCount:
                        urlList[x-1]
                        jiraIssueUrl = getJiraUrl(jiraInstance, jiraToken, repo, urlList[x-1])
                        if jiraIssueUrl:
                            jiraButton = '<a href=' + jiraIssueUrl + ' alt="JIRA Ticket"> <img src="https://img.shields.io/badge/Jira-View%20Jira%20ticket-blue" /></a>'
                            prBody = response[count]['body']
                            if x == 1:
                                updatedPRBody = jiraButton + '\n\n' + prBody
                            else:
                                updatedPRBody = jiraButton + '\n' + updatedPRBody
                            updatePR(owner, repo, pullNumber, updatedPRBody, scmToken)
                            x = x + 1
                        else:
                            print('JIRA ticket not found for PR #' + str(pullNumber) + ' - [' + urlList[x-1] + ']')
                            x = x + 1       
        count = count + 1
    

def extractUrl(str):
    urlRegex = re.compile(r'(http|https):\/\/(snyk|security.snyk)([.]io\/vuln)([\/\w:-]*)')
    url = urlRegex.search(str)
    if url:
        return url.group()

def extractUrls(str):
    regex = '(?:http|https):\/\/(?:snyk|security.snyk)(?:[.]io\/vuln)(?:[\/\w:-]*)'
    match = re.findall(regex, str)
    if len(match) >= 1:
        return match
    else:
        return 0

def getJiraUrl(instance, token, repo, url):    
    if url:
        urlSplit = url.split('/')
        dictLen = len(urlSplit)
        issueRef = urlSplit[dictLen-1]
    else:
        return
    
    endpoint = 'https://' + instance + '/rest/api/3/search'

    headers = {
        'Authorization': 'Basic ' + token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    jqlQuery = 'summary ~ ' + repo + ' AND description ~ ' + issueRef

    body = json.dumps({
        "jql": jqlQuery,
        "fields": ["key"]
    }, indent=None)

    try:
        request = requests.request('POST', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to search for JIRA issue. Error code: ' + str(request.status_code))

    try:
        jiraIssue = response['issues'].pop()
    except:
        return
    else:
        jiraIssueKey = jiraIssue['key']
        jiraUrl = 'https://' + instance + '/browse/' + jiraIssueKey
        return jiraUrl

def updatePR(owner, repo, pullNumber, updatedBody, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/pulls/' + str(pullNumber)
    
    headers = {
        'Authorization': 'token ' + token
    }

    body = json.dumps({
        "body":updatedBody
    })

    try:
        request = requests.request('PATCH', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to update PR. Error code: ' + str(request.status_code))
    else:
        print('PR #' + str(pullNumber) + ' was successfully updated!')

if __name__ == '__main__':
  main()
