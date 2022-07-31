<h3 align="center">
    JIRA PR Editor: Attach your JIRA tickets created via Snyk to already existing PRs.
</h3>

  <img alt="Last commit" src="https://img.shields.io/github/last-commit/snyk-marcos/jira-pr-editor-gh">
</p>

## 🎟️ JIRA PR Editor

Please note this is not an official feature of Snyk. This was created as a hobby to be consumed and maintained by the community.

![JIRA PR Editor](https://github.com/snyk-marcos/repo-images/blob/main/jira-pr-editor/readme_banner.png?raw=true)

### Usage

The recommended use of this script is to be executed in pair with [snyk-tech-services/jira-tickets-for-new-vulns](https://github.com/snyk-tech-services/jira-tickets-for-new-vulns)

To get started, clone the repository and install the necessary dependencies by running: `pip install -r requirements.txt`
> Please note the minimum Python version required to run script is **Version 3.0.0**

:arrow_right: Create a new file named `parameters.txt` following the structure below:

- **`SCM_TOKEN:your-github-token`**
- **`REPO_OWNER:owner-of-github-repo`**
- **`REPO_NAME:name-of-github-repo`**
- **`JIRA_INSTANCE:your-instance.atlassian.net`**
- **`JIRA_TOKEN:your-jira-token`** (Please ensure token is generated as described [here](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/#supply-basic-auth-headers) )

:arrow_right: Place your `parameters.txt` file in the root of the project

:arrow_right: Run the script: `python pr-editor.py`

Please feel free to contribute or suggest features. This is a side-project I am looking forward to maintaining! :blush:

### Screenshots

Once a ticket is found and attached to PR, a label will be created to alert user of ticket(s) present.
<img alt="PR Label" src="https://github.com/snyk-marcos/repo-images/blob/main/jira-pr-editor/pr_list_example.png?raw=true">

---

A button is added to the PR linking back to the JIRA ticket.
<img alt="Trending issues graph" src="https://github.com/snyk-marcos/repo-images/blob/main/jira-pr-editor/pr_details_example.png?raw=true">

---

Made with :heart: by Marcos Bergami
