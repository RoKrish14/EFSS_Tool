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
BASE_URL = https://api.github.com

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

def main():
    try:
        # Retrieve all repositories
        repos = get_repositories(ORGANIZATION_NAME)
        
        # Save repository information to a JSON file
        with open("all_repositories.json", "w") as f:
            json.dump(repos, f, indent=4)
        
        print(f"Retrieved {len(repos)} repositories and saved to 'repositories.json'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
