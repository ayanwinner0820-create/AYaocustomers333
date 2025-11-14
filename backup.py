import os
from datetime import datetime
from git import Repo

def backup_db_to_github(secrets: dict, actor: str='system') -> tuple:
    token = secrets.get('GITHUB_TOKEN')
    repo_full = secrets.get('GITHUB_REPO')
    gh_user = secrets.get('GITHUB_USERNAME')
    if not token or not repo_full or not gh_user:
        return False, 'missing secrets'
    if not os.path.exists('customers.db'):
        return False, 'DB file not exists'
    try:
        repo_url = f'https://{gh_user}:{token}@github.com/{repo_full}.git'
        tmpdir = '/tmp/ayaobackup'
        if os.path.exists(tmpdir):
            import shutil
            shutil.rmtree(tmpdir)
        Repo.clone_from(repo_url, tmpdir)
        import shutil
        stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        dst = os.path.join(tmpdir, 'backups', f'customers_{stamp}.db')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile('customers.db', dst)
        repo = Repo(tmpdir)
        repo.git.add(all=True)
        repo.index.commit(f'backup db {stamp} by {actor}')
        origin = repo.remote(name='origin')
        origin.push()
        return True, 'ok'
    except Exception as e:
        return False, str(e)
