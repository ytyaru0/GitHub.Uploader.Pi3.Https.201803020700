#!python3
#encoding:utf-8
import os.path
import subprocess
import database.license.insert.command.miscellaneous.Licenses
class Main:
    def __init__(self, db, client):
        self.__db = db
        self.__client = client
        self.__licenses = database.license.insert.command.miscellaneous.Licenses.Licenses(self.__db, self.__client)

    def Initialize(self):
        self.__InsertForFile()

    def Run(self):
        license_key = 'start'
        while '' != license_key:
            print('入力したKeyのライセンスを問い合わせます。(未入力+Enterで終了)')
            print('サブコマンド    l:既存リポジトリ m:一覧更新  f:ファイルから1件ずつ挿入')
            key = input()
            if '' == key:
                break
            elif 'l' == key or 'L' == key:
                self.__licenses.Show()
            elif 'f' == key or 'F' == key:
                self.__InsertForFile()
            elif 'm' == key or 'M' == key:
                self.__licenses.Update()
            else:
                self.__licenses.InsertOne(key)

    def __InsertForFile(self):
        file_name = 'LicenseKeys.txt'
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
        if not(os.path.isfile(file_path)):
            print(file_name + 'ファイルを作成し、1行ずつキー名を書いてください。')
            return
        with open(file_path, mode='r', encoding='utf-8') as f:
            for line in f:
                print(line.strip())
                self.__licenses.InsertOne(line.strip())

    """
    def __GetClient(self, username=None):
        if None is username: account = self.__dbs['account']['Accounts'].find().next()
        else:                account = self.__dbs['account']['Accounts'].find_one(Username=username)
        twofactor = self.__dbs['account']['TwoFactors'].find_one(AccountId=account['Id'])
        authentications = []
        if None is not twofactor:
            authentications.append(TwoFactorAuthentication(account['Username'], account['Password'], twofactor['Secret']))
        else:
            authentications.append(BasicAuthentication(account['Username'], account['Password']))
        return web.service.github.api.v3.Client.Client(self, authentications)
    """

