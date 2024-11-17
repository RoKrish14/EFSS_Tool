import requests
import json
import os
import time

# set up authentication and configuration for interacting with the GitHub API
GITHUB_TOKEN = os.getenv('NEW_TOKEN')
ORGANIZATION_NAMES = ['eclipse-tractusx', 'eclipse-cbi']

# url = f"https://api.github.com/orgs/{ORGANIZATION_NAMES}/repos"
# response = requests.get(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
# print(response.status_code, response.json())

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
        if handle_rate_limit(response):
            continue  # Retry after handling rate limit
        if response.status_code != 200:
            raise Exception(f"Error fetching repositories {org_name}: {response.json()}")
        
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
    
    if handle_rate_limit(response):
        return check_secret_scanning(repo_full_name)  # Retry after handling rate limit

    if response.status_code == 200:
        return True  # Secret scanning is enabled
    elif response.status_code == 404:
        return False  # Secret scanning not available for this repo
    elif response.status_code == 304:
        return "Unchanged" # no changed data from before
    elif response.status_code == 403:
        print(f"Access denied for {repo_full_name}. Check permissions.")
        return False  # Permissions issue
    else:
        raise Exception(f"Error checking secret scanning for {repo_full_name}: {response.text}")

def handle_rate_limit(response, max_retries=5):
    if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        if remaining == 0:
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
            sleep_time = reset_time - int(time.time())
            # pause to handle rate limit if needed
            # print(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
            # time.sleep(sleep_time + 1)
            #return True
            retries = 0
            while retries < max_retries:
                # Exponential backoff: 2^n where n is the retry count
                backoff_time = min(sleep_time + 2 ** retries, 3600)  # cap backoff time at 1 hour
                print(f"Rate limit reached. Sleeping for {backoff_time} seconds... (Retry {retries + 1}/{max_retries})")
                time.sleep(backoff_time)
                response = requests.get(response.url, headers=headers)
                if response.status_code != 403:  # Exit if rate limit is not exceeded
                    return False
                retries += 1
            # If maximum retries are exceeded, raise an exception
            raise Exception("Exceeded maximum retries while waiting for rate limit reset.")            
    return False

def main():
  for org_name in ORGANIZATION_NAMES:
        print(f"Checking repositories for organization: {org_name}")
        org_results = {}  # Store results for this organization
        
        try:
            repos = get_repositories(org_name)
        except Exception as e:
            print(f"Failed to fetch repositories for {org_name}: {e}")
            continue
        
        for repo in repos:
            repo_name = repo["full_name"]
            try:
                secret_scanning_enabled = check_secret_scanning(repo_name)
                org_results[repo_name] = secret_scanning_enabled
                status = "enabled" if secret_scanning_enabled else "not enabled"
                print(f"Secret scanning is {status} for repository {repo_name}.")
            except Exception as e:
                print(f"Failed to check secret scanning for {repo_name}: {e}")
        
        # Save results for this organization to a JSON file
        file_name = f"{org_name}_secret_scanning_results.json"
        with open(file_name, "w") as f:
            json.dump(org_results, f, indent=4)

        print(f"Results saved to {file_name}.")
        # Sleep to avoid hitting rate limits unnecessarily
        time.sleep(1)

if __name__ == "__main__":
    main()
