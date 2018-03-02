#!python3
#encoding:utf-8
import os.path
from cui.uploader.command.repository.Creator import Creator
from cui.uploader.command.repository.Commiter import Commiter
from cui.uploader.command.repository.Deleter import Deleter
from cui.uploader.command.repository.Editor import Editor
from cui.uploader.command.aggregate.Aggregate import Aggregate
from web.log.Log import Log
from database.Database import Database as Db

class Main:
    def __init__(self, client, args):
        self.__client = client
        self.__args = args

        self.__creator = Creator(self.__client, self.__args)
        self.__commiter = Commiter(self.__client, self.__args)
        self.__deleter = Deleter(self.__client, self.__args)
        self.__editor = Editor(self.__client, self.__args)
        self.__agg = Aggregate(self.__args)

        self.__account = Db().Accounts['Accounts'].find_one(Username=self.__args.username)
        self.__ssh_configures = Db().Accounts['SshConfigures'].find_one(AccountId=self.__account['Id'])
        self.__repo_name = os.path.basename(self.__args.path_dir_pj)
        self.__repos = Db().Repositories[self.__args.username]['Repositories'].find_one(Name=self.__repo_name)

    def Run(self):
        if -1 != self.__Create():
            if None is self.__repos: self.__repos = Db().Repositories[self.__args.username]['Repositories'].find_one(Name=self.__repo_name)
            self.__Commit()

    def __CreateInfo(self):
        Log().Logger.info('ユーザ名: {0}'.format(self.__account['Username']))
        Log().Logger.info('メアド: {0}'.format(self.__account['MailAddress']))
        Log().Logger.info('SSH HOST: {0}'.format(self.__ssh_configures['HostName']))
        if None is self.__repos:
            Log().Logger.info('リポジトリ名: {0}'.format(self.__repo_name))
            Log().Logger.info('説明: {0}'.format(self.__args.description))
            Log().Logger.info('URL: {0}'.format(self.__args.homepage))
        else:
            Log().Logger.info('リポジトリ名: {0}'.format(self.__repos['Name']))
            Log().Logger.info('説明: {0}'.format(self.__repos['Description']))
            Log().Logger.info('URL: {0}'.format(self.__repos['Homepage']))
        Log().Logger.info('リポジトリ情報は上記のとおりで間違いありませんか？[y/n]')

    def __Create(self):
        if os.path.exists(os.path.join(self.__args.path_dir_pj, ".git")):
            if self.__repos is None:
                msg = "整合性エラー。 .git が存在するのにDBには存在しません。\nコピペで別の .git を使い回していませんか？\nまたは本ツールを使わずに .git を作成しませんでしたか？\n\n解法は2つあります。\n１．既存リモートリポジトリをDBに取り込む\n２．既存のローカルとリモートの両リポジトリを削除して本ツールでアップロードし直す（git履歴が消える）\n\n１はまず既存のAccountsDBを削除します。次にユーザ作成することで既存リモートリポジトリがDBに登録されます。それで整合性エラーが解決します。その後、再度Uploader.pyを再試行してください。"
                raise Exception(msg)
            else: return 0
        answer = ''
        while '' == answer:
            self.__CreateInfo()
            answer = input()
            if 'y' == answer or 'Y' == answer:
                self.__creator.Create()
                return 0
            elif 'n' == answer or 'N' == answer:
                Log().Logger.info('call.shを編集して再度やり直してください。')
                return -1
            else:
                answer = ''

    def __CommitInfo(self):
        Log().Logger.info('リポジトリ名： {0}/{1}'.format(self.__account['Username'], self.__repos['Name']))
        Log().Logger.info('説明: {0}'.format(self.__repos['Description']))
        Log().Logger.info('URL: {0}'.format(self.__repos['Homepage']))
        Log().Logger.info('----------------------------------------')
        self.__commiter.ShowCommitFiles()
        Log().Logger.info('commit,pushするならメッセージを入力してください。Enterかnで終了します。')
        Log().Logger.info('サブコマンド    n:終了 a:集計 e:編集 d:削除 i:Issue作成')
    
    def __Commit(self):
        # 起動引数-mが未設定だとNoneになる。そのときはcommitとIssueの同時登録はしない。
        if None is not self.__args.messages:
            self.__commiter.AddCommitPushIssue(self.__args.messages)
            self.__agg.Show()
        else:
            while (True):
                self.__CommitInfo()
                answer = input()
                if '' == answer or 'n' == answer or 'N' == answer:
                    Log().Logger.info('終了します。')
                    break
                elif 'a' == answer or 'A' == answer:
                    self.__agg.Show()
                elif 'e' == answer or 'E' == answer:
                    self.__ConfirmEdit()
                elif 'd' == answer or 'D' == answer:
                    self.__ConfirmDelete()
                    break
                elif 'i' == answer or 'I' == answer:
                    Log().Logger.info('(Issue作成する。(未実装))')
                else:
                    self.__commiter.AddCommitPush(answer)
                    self.__agg.Show()

    def __ConfirmDelete(self):
        Log().Logger.info('.gitディレクトリ、対象リモートリポジトリ、対象DBレコードを削除します。')
        Log().Logger.info('リポジトリ名： {0}/{1}'.format(self.__account['Username'], self.__repos['Name']))
        self.__deleter.ShowDeleteRecords()
        Log().Logger.info('削除すると復元できません。本当に削除してよろしいですか？[y/n]')
        answer = input()
        if 'y' == answer or 'Y' == answer:
            self.__deleter.Delete()
            Log().Logger.info('削除しました。')
            return True
        else:
            Log().Logger.info('削除を中止しました。')
            return False

    def __ConfirmEdit(self):
        Log().Logger.info('編集したくない項目は無記入のままEnterキー押下してください。')
        Log().Logger.info('リポジトリ名を入力してください。')
        name = input()
        # 名前は必須項目。変更しないなら現在の名前をセットする
        if None is name or '' == name: name = self.__repos['Name']
        Log().Logger.info('説明文を入力してください。')
        description = input()
        Log().Logger.info('Homepageを入力してください。')
        homepage = input()
        
        if '' == description and '' == homepage and self.__repos['Name'] == name:
            Log().Logger.info('編集する項目がないため中止します。')
        else:
            self.__editor.Edit(name, description, homepage)
            Log().Logger.info('編集しました。')
