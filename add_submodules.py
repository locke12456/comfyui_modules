import os
import subprocess

def is_git_repo(path):
    """檢查指定路徑是否為 Git repository"""
    return os.path.isdir(os.path.join(path, '.git'))

def get_remote_url(path):
    """取得 Git repository 的遠端 URL"""
    try:
        result = subprocess.run(
            ['git', '-C', path, 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_current_commit(path):
    """取得當前 Git repository 的 HEAD commit"""
    try:
        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def add_submodule(main_repo_path, submodule_path, remote_url):
    """將子資料夾新增為 submodule"""
    try:
        subprocess.run(
            ['git', '-C', main_repo_path, 'submodule', 'add', remote_url, submodule_path],
            check=True
        )
        print(f"已新增 {submodule_path} 作為 submodule。")
    except subprocess.CalledProcessError as e:
        print(f"新增 submodule 時出錯：{e}")

def record_commit(main_repo_path):
    """記錄當前所有 submodule 的 commit 狀態並提交變更"""
    try:
        # 更新所有 submodule 的狀態到最新 commit
        subprocess.run(
            ['git', '-C', main_repo_path, 'submodule', 'update', '--init', '--recursive'],
            check=True
        )

        # 提交變更
        subprocess.run(
            ['git', '-C', main_repo_path, 'add', '.gitmodules'],
            check=True
        )
        subprocess.run(
            ['git', '-C', main_repo_path, 'add', '.'],
            check=True
        )
        subprocess.run(
            ['git', '-C', main_repo_path, 'commit', '-m', 'Add submodules and record their commit states'],
            check=True
        )
        print("已記錄所有 submodule 的狀態並提交變更。")
    except subprocess.CalledProcessError as e:
        print(f"記錄 submodule 狀態時出錯：{e}")

def main():
    main_repo_path = "./"  # 替換為您的主倉庫路徑
    os.chdir(main_repo_path)

    # 確認主資料夾為 Git repository
    if not is_git_repo(main_repo_path):
        print("這個資料夾還不是一個 Git 倉庫，請先初始化： git init")
        return

    # 遍歷當前資料夾中的所有子資料夾
    for folder in os.listdir(main_repo_path):
        folder_path = os.path.join(main_repo_path, folder)
        if os.path.isdir(folder_path) and is_git_repo(folder_path):
            remote_url = get_remote_url(folder_path)
            if remote_url:
                add_submodule(main_repo_path, folder, remote_url)
            else:
                print(f"{folder} 沒有遠端 URL，無法新增為 submodule。")
    
    # 記錄所有 submodule 的 commit 狀態並提交變更
    record_commit(main_repo_path)

if __name__ == "__main__":
    main()
