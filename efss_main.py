import requests
import json
import os

# set up authentication and configuration for interacting with the GitHub API
GITHUB_TOKEN = os.getenv('NEW_TOKEN')
ORGANIZATION_NAME = 'eclipse-tractusx'

url = f"https://api.github.com/orgs/{ORGANIZATION_NAME}/repos"
response = requests.get(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
print(response.status_code, response.json())

# Base URL for GitHub API
BASE_URL = "https://api.github.com"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Retreive all the repos from the org
def get_repositories(org_name):
  # url = https://api.github.com/orgs/eclipse-tractusx/repos
    url = f"{BASE_URL}/orgs/{org_name}/repos"
    repos = []
    page = 1
    
    while True:
        response = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            raise Exception(f"Error fetching repositories: {response.json()}")
        
        page_data = response.json()
        if not page_data:  # Exit loop if no more repositories
            break
        
        repos.extend(page_data)
        page += 1  # Go to next page
    
    return repos

# Check if secret scanning is enabled
def check_secret_scanning(repo_full_name):
    url = f"{BASE_URL}/repos/{repo_full_name}/secret-scanning/alerts"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return True
    elif response.status_code == 403:
        return False  # Secret scanning not enabled or permissions issue
    else:
        raise Exception(f"Error checking secret scanning for {repo_full_name}: {response.json()}")

def main():
    try:
        # Fetch all repositories in the organization
        repos = get_repositories(ORGANIZATION_NAME)
        results = {}

        for repo in repos:
            repo_name = repo["full_name"]
            try:
                # Check secret scanning for the repository
                secret_scanning_enabled = check_secret_scanning(repo_name)
                results[repo_name] = secret_scanning_enabled
                status = "enabled" if secret_scanning_enabled else "not enabled"
                print(f"Secret scanning is {status} for repository {repo_name}.")
            except Exception as e:
                print(f"Failed to check secret scanning for {repo_name}: {e}")
        
        # Save results to a JSON file
        with open("all_repositories.json", "w") as f:
            json.dump(results, f, indent=4)
        
        print("Results saved to 'all_repositories.json'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
