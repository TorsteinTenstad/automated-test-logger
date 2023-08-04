import git
import pathlib
import __main__


class GitInfo:
    def __init__(self):
        repo = git.Repo(search_parent_directories=True)
        self.git_hash = repo.head.object.hexsha
        self.git_url = repo.remotes.origin.url
        self.git_local_dir = pathlib.Path(repo.git_dir).parent
        self.is_dirty = repo.is_dirty() or any([untracked_file.endswith(pathlib.Path(__main__.__file__).name) for untracked_file in repo.untracked_files])


if __name__ == '__main__':
    git_info = GitInfo()
    print(git_info.git_hash)
    print(git_info.git_url)
    print(git_info.git_local_dir)
    print(git_info.is_dirty)