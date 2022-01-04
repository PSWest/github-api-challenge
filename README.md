# github-api-challenge
__Mentat Submission For Github API Challenge__

This is a Python based webhook hosted with [Azure Functions](https://azure.microsoft.com/en-us/services/functions/) with [GitHub API v4](https://docs.github.com/en/rest). The function triggers on a Post  when a GitHub repo is created, and this will trigger the Python function to add branch protection to the `'main'` branch.

### Retreive A GitHub Personal Auth Token
To use this function you should have a GitHub personal auth token and a GitHub account.
Learn how retreive a GitHub Personal Auth Token click [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

### Setup An Azure Serverless Function
Lets setup an Azure function:
To do this follow the steps outlined [here](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)
To deploy this function from this GitHub repo follow [these steps](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-github-actions?tabs=python)

Once this is done you should add four params to your function settings configuration to pass Global paramas as Environment variables.
These params should be added individually in your Azure Settings Configuration as Keys and Values:
```
    "User": "MyUserName",
    "GitHubToken": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "OrgName": "MyOrganizationName",
    "BranchName": "MyBranchName"
```
To learn how to set environment variables for your function click [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal#settings)

To test this on your local you should add the same value to your `local.settings.json` file/
To learn how to set your `local.settings.json` check [this article](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local#local-settings-file).
Your `local.settings.json` should look like this:
```{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "User": "MyUserName",
    "GitHubToken": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "OrgName": "MyOrganizationName",
    "BranchName": "MyBranchName"
  }
}
```
### Fetch Your Azure Function Key
To get your functions access key read [this](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal#get-your-function-access-keys) part of the article.

### Get your Azure Function Public URL
Fetch your Azure Function API public URL:
To learn how to fetch the public URL of your Azure Function please see [this article](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=python#get-the-url-of-the-deployed-function)

### Setup A GitHub Organization WebHook
Next we need to create a GitHub WebHook at the Organization level.
To create an organization WebHook follow [this guide](https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks)
This WebHook should trigger when a 'Repository' is created.
Ensure to use your Azure Function Public URL from the step above. Also, fetch and include your funcitons key as the 'Secret' when configuring your WebHook.

### Test your function
You can test this function by creating GitHub repo with a ReadMe.md from GitHub's website.


