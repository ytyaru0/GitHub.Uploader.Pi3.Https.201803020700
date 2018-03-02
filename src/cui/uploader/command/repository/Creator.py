#!python3
#encoding:utf-8
import os.path
from setting.Config import Config
from database.Database import Database as Db
import cui.sh.Client

class Creator:
    def __init__(self, client, args):
        self.__client = client
        self.__args = args
        self.__userRepo = Db().Repositories[self.__args.username]
        self.__repo_name = os.path.basename(self.__args.path_dir_pj)

    def Create(self):
        self.__LoadDb()
        self.__CreateLocalRepository()
        j = self.__client.Repositories.create(self.__repo_name, description=self.__args.description, homepage=self.__args.homepage)
        self.__InsertRemoteRepository(j)

    def __LoadDb(self):
        self.__account = Db().Accounts['Accounts'].find_one(Username=self.__args.username)
        if None is self.__account: raise Exception('未登録のアカウントです。登録してから再度実行してください。')
        self.__sshconfigures = Db().Accounts['SshConfigures'].find_one(AccountId=self.__account['Id'])

    def __CreateLocalRepository(self):
        client = cui.sh.Client.Client(cwd=self.__args.path_dir_pj)
        client.run("git init")
        client.run("git config --local user.name '{0}'".format(self.__args.username))
        client.run("git config --local user.email '{0}'".format(self.__account['MailAddress']))
        client.run("git remote add origin {0}".format(Config()['Git']['Remote'].GetRepositoryUri(self.__args.username, self.__repo_name)))

    def __InsertRemoteRepository(self, j):
        self.__userRepo.begin()
        repo = self.__userRepo['Repositories'].find_one(Name=j['name'])
        # Repositoriesテーブルに挿入する
        if None is repo:
            self.__userRepo['Repositories'].insert(self.__CreateRecordRepositories(j))
            repo = self.__userRepo['Repositories'].find_one(Name=j['name'])
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.__userRepo['Repositories'].update(self.__CreateRecordRepositories(j), ['Name'])

        # Countsテーブルに挿入する
        cnt = self.__userRepo['Counts'].count(RepositoryId=repo['Id'])
        if 0 == cnt:
            self.__userRepo['Counts'].insert(self.__CreateRecordCounts(self.__userRepo['Repositories'].find_one(Name=j['name'])['Id'], j))
        # 何らかの原因でローカルDBに既存の場合はそのレコードを更新する
        else:
            self.__userRepo['Counts'].update(self.__CreateRecordCounts(repo['Id'], j), ['RepositoryId'])
        self.__userRepo.commit()

    def __CreateRecordRepositories(self, j):
        import datetime
        import pytz
        return dict(
            IdOnGitHub=j['id'],
            Name=j['name'],
            Description=j['description'],
            Homepage=j['homepage'],
            CreatedAt=j['created_at'],
            PushedAt=j['pushed_at'],
            UpdatedAt=j['updated_at'],
            CheckedAt="{0:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(pytz.utc))
        )

    def __CreateRecordCounts(self, repo_id, j):
        return dict(
            RepositoryId=repo_id,
            Forks=j['forks_count'],
            Stargazers=j['stargazers_count'],
            Watchers=j['watchers_count'],
            Issues=j['open_issues_count']
        )

