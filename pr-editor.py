import os
import sys
import requests
import json
import re
import pyfiglet
from rich import print as rprint

def main():
    
    checkSysVersion()

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

    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/pulls?state=all&per_page=100'

    headers = {
        'Authorization': 'token ' + scmToken
    }

    values = ''
    
    request = requests.request('GET', endpoint, headers=headers, data=values)
    response = request.json()
    
    count = 0
    x = 0

    title = pyfiglet.figlet_format("JIRA PR Editor", font="slant")
    rprint("[bold blue]" + title)
    print('ATTACH YOUR JIRA TICKETS CREATED VIA SNYK TO ALREADY EXISTING PRS\n \n')

    checkRepoLabels(owner, repo, scmToken)

    while count < len(response):        
        if '[Snyk]' in response[count]['title']:
            if 'Jira' not in response[count]['body']:
                pullNumber = response[count]['number']
                urlList = extractUrls(response[count]['body'])
                if urlList:
                    urlCount = len(urlList)
                    x = 1
                    updatedPRBody = ''
                    updatedPRTitle = ''
                    while x <= urlCount:
                        urlList[x-1]
                        result = getJiraUrl(jiraInstance, jiraToken, repo, urlList[x-1])
                        try:                      
                            jiraIssueUrl, jiraIssueKey = result
                        except:
                            jiraIssueUrl = None
                        if jiraIssueUrl:
                            jiraButton = '<a href=' + jiraIssueUrl + ' alt="JIRA Ticket"> <img src="https://img.shields.io/badge/Jira-View%20Jira%20ticket-blue" /></a>'
                            prBody = response[count]['body']
                            prTitle = response[count]['title']
                            if x == 1:
                                updatedPRBody = jiraButton + '\n\n' + prBody
                                updatedPRTitle = prTitle + ' - [' + jiraIssueKey + ']'
                            else:
                                updatedPRBody = jiraButton + '\n' + updatedPRBody
                                updatedPRTitle = updatedPRTitle + ' - [' + jiraIssueKey + ']'
                            updatePR(owner, repo, pullNumber, updatedPRBody, updatedPRTitle, scmToken)
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
        return jiraUrl, jiraIssueKey


def updatePR(owner, repo, prNumber, updatedBody, updatedTitle, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/pulls/' + str(prNumber)
    
    headers = {
        'Authorization': 'token ' + token
    }

    body = json.dumps({
        "title":updatedTitle,
        "body":updatedBody
    })

    try:
        request = requests.request('PATCH', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to update PR. Error code: ' + str(request.status_code))
    else:
        ret = checkPRLabel(owner, repo, prNumber, token)
        if ret == 0:
            print('PR #' + str(prNumber) + ' was successfully updated!')
        else:
            print('Failed to update PR. Please try again')

def checkRepoLabels(owner, repo, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/labels'
    
    headers = {
        'Authorization': 'token ' + token
    }

    body = ''

    count = 0
    hasLabel = 0

    try:
        request = requests.request('GET', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to get repo labels. Error code: ' + str(request.status_code))
    else:
        while count < len(response):
            if 'JIRA' in response[count]['name']:
                hasLabel = 1
                break
            count = count + 1
        
        if hasLabel == 0:
            createLabel(owner, repo, token)

def createLabel(owner, repo, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/labels'

    headers = {
        'Authorization': 'token ' + token
    }

    body = json.dumps({
        "name": "JIRA",
        "description": "A ticket has been created in JIRA for this PR",
        "color": "0052CC",
    })

    try:
        request = requests.request('POST', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to get repo labels. Error code: ' + str(request.status_code))
    else:
        print('Label successfully created!')
        return 0

def checkPRLabel(owner, repo, prNumber, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/' + 'issues/' + str(prNumber) + '/labels'

    headers = {
        'Authorization': 'token ' + token
    }

    body = ''
    count = 0
    hasLabel = 0

    try:
        request = requests.request('GET', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to get PR labels. Error code: ' + str(request.status_code))
    else:
        while count < len(response):
            if 'JIRA' in response[count]['name']:
                hasLabel = 1
                return 0     
        
        if hasLabel == 0:
            ret = addLabelToPR(owner, repo, prNumber, token)
            if ret == 0:
                return 0           

def addLabelToPR(owner, repo, prNumber, token):
    endpoint = 'https://api.github.com/repos/' + owner + '/' + repo + '/' + 'issues/' + str(prNumber) + '/labels'

    headers = {
        'Authorization': 'token ' + token
    }

    body = json.dumps({
        "labels":["JIRA"]
    })

    try:
        request = requests.request('POST', endpoint, headers=headers, data=body)
        response = request.json()
    except:
        print('Failed to add PR label. Error code: ' + str(request.status_code))
    else:
        return 0      

def checkSysVersion():
    minVersion = (3, 0)
    if not sys.version_info >= minVersion:
        raise EnvironmentError(
            "Python version too low, required at least {}".format('.'.join(str(n) for n in minVersion)))

if __name__ == '__main__':
  main()
