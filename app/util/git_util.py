import git
import os
import subprocess
from urllib.parse import urlparse

def get_authenticated_url(url: str, token: str) -> str:
    """
    Robustly converts any Git URL (SSH or HTTPS) to an authenticated HTTPS URL.
    Input:  git@github.com:user/repo.git  OR  https://github.com/user/repo.git
    Output: https://TOKEN@github.com/user/repo.git
    """
    clean_url = url.strip()
    
    # 1. Handle SSH SCP-style URLs (git@github.com:user/repo.git)
    if clean_url.startswith("git@"):
        # Convert the ':' before the path to a '/'
        clean_url = clean_url.replace(":", "/", 1)
        # Remove the 'git@' prefix
        clean_url = clean_url.replace("git@", "", 1)
    
    # 2. Handle standard schemes (https:// or ssh://)
    elif "://" in clean_url:
        # Strip scheme (https://)
        clean_url = clean_url.split("://")[-1]
        
    # 3. Clean up any existing auth (user:pass@domain.com)
    if "@" in clean_url:
        clean_url = clean_url.split("@")[-1]

    # 4. Rebuild as HTTPS with the token
    return f"https://{token}@{clean_url}"

def clone_or_pull_repository(repo_url: str, directory: str) -> str | None:
    # Set safe.directory to avoid permission errors. This will run inside the container.
    try:
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "*"], check=True)
    except Exception as e:
        print(f"Failed to set safe.directory: {e}")

    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_ACCESS_TOKEN environment variable is not set")

    # 1. Determine local path
    # Extract "my-repo" from "https://github.com/user/my-repo.git"
    repo_name = os.path.basename(repo_url.rstrip("/")).replace(".git", "")
    base_dir = os.path.join(os.getcwd(), "repositories")
    repo_path = os.path.join(base_dir, repo_name)
    
    # 2. Get the Authenticated URL
    # We use this for cloning, but standard 'pull' operations usually 
    # reuse the config in .git/config. If that config doesn't have the token,
    # you might need to update the remote URL.
    auth_url = get_authenticated_url(repo_url, token)

    # 3. Clone or Pull
    try:
        if os.path.exists(repo_path):
            print(f"Repository exists at {repo_path}. Pulling...")
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            # Optional: Update remote URL to ensure token is current
            origin.set_url(auth_url)
            origin.pull()
        else:
            print(f"Cloning to {repo_path}...")
            os.makedirs(base_dir, exist_ok=True)
            repo = git.Repo.clone_from(auth_url, repo_path)
        return repo_path
    except git.exc.GitCommandError as e:
        print(f"Git Error (Check permissions/token): {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def commit_and_push_repository(repo_url: str, directory: str):
    # Set safe.directory to avoid permission errors. This will run inside the container.
    try:
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "*"], check=True)
    except Exception as e:
        print(f"Failed to set safe.directory: {e}")

    repo_name = os.path.basename(repo_url.rstrip("/")).replace(".git", "")
    base_dir = os.path.join(os.getcwd(), "repositories")
    repo_path = os.path.join(base_dir, repo_name)

    repo = git.Repo(repo_path)

    # 5. Commit and Push
    if repo.is_dirty(untracked_files=True):
        print("Changes detected. Committing and pushing...")
        
        # 'A=True' is equivalent to 'git add -A' (stages all changes/deletions)
        repo.git.add(A=True) 
        
        repo.index.commit("Automated update after processing")
        
        try:
            repo.remotes.origin.push()
            print("Push successful.")
        except git.exc.GitCommandError as e:
            print(f"Failed to push: {e}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No changes detected. Nothing to push.")
