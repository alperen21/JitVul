import subprocess
import os 

class Cloner:
    def __init__(self, projects_dir : str = "projects"):
        self.path = "repo"
        self.projects_dir = projects_dir
        
    def clone(self, url : str, path : str = 'repo') -> None:
        self.path = path
        subprocess.run(["git", "clone", url, os.path.join(self.projects_dir, path)], capture_output=True)
    
    def checkout(self, commit_id : str) -> None:
        subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git checkout {commit_id}", shell=True, capture_output=True)
    
    def checkout_to_vulnerable(self, commit_id : str) -> None:
        subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git checkout {commit_id}  && git checkout HEAD^", shell=True, capture_output=True)
    
    def checkout_to_benign(self,  commit_id : str) -> None:
        subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git checkout {commit_id}", shell=True, capture_output=True)
        
    def remove_repo(self) -> None:
        try:            
            subprocess.run(f"rm -rf {os.path.join(self.projects_dir, self.path)}", shell=True, capture_output=True)
        except Exception as e:
            print("Repository doesn't exist")
            
    def get_current_commit_id(self) -> str:
        result = subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git rev-parse HEAD", shell=True, capture_output=True)
        return result.stdout.decode().strip()
    
    def get_current_commit_url(self) -> str:
        result = subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git config --get remote.origin.url", shell=True, capture_output=True)
        return result.stdout.decode().strip()
    
    def get_current_commit_message(self) -> str:
        result = subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git log -1 --pretty=%B", shell=True, capture_output=True)
        return result.stdout.decode().strip()
    
    def go_back_one_commit(self) -> None:
        subprocess.run(f"cd {os.path.join(self.projects_dir, self.path)} && git checkout HEAD^", shell=True, capture_output=True)