#!python3
#encoding:utf-8
import os.path
from setting.Config import Config
import argparse
from database.Database import Database as Db
import pyotp
import pyperclip
from web.log.Log import Log

class GitHubOtpCreator:
    def __init__(self):
        self.__path_dir_this = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    def Create(self):
        self.__totp = pyotp.TOTP(self.__GetUserSecret())
        Log().Logger.info("otp = {0}".format(self.__totp.now()))
        pyperclip.copy(self.__totp.now())
    
    def __GetUserSecret(self):
        parser = argparse.ArgumentParser(
            description='GitHub Repository Uploader.',
        )
        parser.add_argument('-u', '--username', '--user')
        args = parser.parse_args()
        
        username = args.username
        if None is username:
            if not('GitHub' in Config()):
                raise Exception('ユーザ名が必要です。しかし起動引数にもconfig.iniにも存在しません。起動引数なら第一引数にユーザ名を渡してください。yamlならGithub.Userキーにユーザ名を指定してください。')
            if not('User' in Config()['Github']):
                raise Exception('ユーザ名が必要です。しかし起動引数にもconfig.iniにも存在しません。起動引数なら第一引数にユーザ名を渡してください。yamlならGithub.Userキーにユーザ名を指定してください。')
            username = Config()['Github']['User']

        Log().Logger.info("username = {0}".format(username))
        account = Db().Accounts['Accounts'].find_one(Username=username)
        if None is account:
            raise Exception('ユーザ {0} はDBのAccountsテーブルに存在しません。登録してから再度実行してください。'.format(username))
        twofactor = Db().Accounts['TwoFactors'].find_one(AccountId=account['Id'])
        if None is twofactor:
            raise Exception('ユーザ {0} はDBのTwoFactorsテーブルに存在しません。登録してから再度実行してください。'.format(username))
        return twofactor['Secret']


if __name__ == '__main__':
    c = GitHubOtpCreator()
    c.Create()
