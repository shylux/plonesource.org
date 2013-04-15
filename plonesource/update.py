from datetime import datetime
from plonesource.config import CONFIG
from pygithub3 import Github
import os


GITHUB = Github()

OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..',
                 'static', 'sources.cfg'))

TIMESTAMP_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..',
                 'static', 'last-update.txt'))


def update(principals, repos):
    repositories = {}

    for principal in principals:
        load_principal_repositories(principal, repositories)

    for fullname in repos:
        load_single_repositories(fullname, repositories)

    return generate_sources_cfg(repositories)


def load_principal_repositories(principal, result):
    for repo in GITHUB.repos.list(principal).all():
        result[repo.name] = extract_repo_data(repo)


def load_single_repositories(fullname, result):
    username, reponame = fullname.split('/')
    repo = GITHUB.repos.get(user=username, repo=reponame)
    result[repo.name] = extract_repo_data(repo)


def extract_repo_data(repo):
    return {'name': repo.name,
            'clone_url': repo.clone_url,
            'push_url': repo.ssh_url,
            'branch': repo.master_branch}



def generate_sources_cfg(repositories):
    branches = []
    sources = []

    for _name, item in repositories.items():
        branches.append('%(name)s = %(branch)s' % item)
        sources.append('%(name)s = git %(clone_url)s pushurl=%(push_url)s'
                       ' branch=${branches:%(name)s}' % item)

    lines = [
        '[buildout]',
        'auto-checkout =',
        'sources = sources',
        '',
        '[branches]'] + \
        sorted(branches) + [
        '',
        ''
        '[sources]'] + \
        sorted(sources) + [
        '']

    return '\n'.join(lines)


def main():
    data = update(reversed(CONFIG.get('principals')),
                  CONFIG.get('repos'))
    with open(OUTPUT_PATH, 'w+') as file_:
        file_.write(data)

    with open(TIMESTAMP_PATH, 'w+') as file_:
        file_.write(datetime.now().isoformat())

    print 'Updated'
