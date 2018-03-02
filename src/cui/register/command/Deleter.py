#!python3
#encoding:utf-8
import os.path
from database.Database import Database as Db
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
import web.service.github.api.v3.Client
import cui.register.command.ASubCommand
from web.log.Log import Log

class Deleter(cui.register.command.ASubCommand.ASubCommand):
    def __init__(self, path_dir_root):
        self.__path_dir_root = path_dir_root

    def Run(self, args):
        Log().Logger.debug('Account.Delete')
        Log().Logger.debug(args)
        Log().Logger.debug('-u: {0}'.format(args.username))
        Log().Logger.debug('--auto: {0}'.format(args.auto))
        
        account = Db().Accounts['Accounts'].find_one(Username=args.username)
        Log().Logger.debug(account)

        if None is account:
            Log().Logger.warning('指定したユーザ {0} がDBに存在しません。削除を中止します。'.format(args.username))
            return
        else:
            authentications = []
            twofactor = Db().Accounts['TwoFactors'].find_one(AccountId=account['Id'])
            if None is not twofactor:
                authentications.append(TwoFactorAuthentication(account['Username'], account['Password'], twofactor['Secret']))
            else:
                authentications.append(BasicAuthentication(account['Username'], account['Password']))
            client = web.service.github.api.v3.Client.Client(authentications)
            
            # 1. 指定ユーザの全Tokenを削除する（SSHKey設定したTokenのはずなのでSSHKeyも削除される
            self.__DeleteToken(account, client)
            # 2. SSHのconfigファイル設定の削除と鍵ファイルの削除
            self.__DeleteSshFile(account['Id'])
            # 3. DB設定値(Account, Repository)
            self.__DeleteDatabase(account)
            # * GitHubアカウントの退会はサイトから行うこと

    def __DeleteToken(self, account, client):
        # 1. Tokenの新規作成
        for token in Db().Accounts['AccessTokens'].find(AccountId=account['Id']):
            client.Authorizations.Delete(token['IdOnGitHub'])

    def __DeleteSshFile(self, account_id):
        sshconfigure = Db().Accounts['SshConfigures'].find_one(AccountId=account_id)
        if None is sshconfigure:
            return
        hostname = sshconfigure['HostName']
        sshconf = cui.register.SshConfigurator.SshConfigurator()
        sshconf.Load()
        # SSH鍵ファイル削除
        path_private = sshconf.GetPrivateKeyFilePath(hostname)
        path_public = sshconf.GetPublicKeyFilePath(hostname)
        if os.path.isfile(path_private):
            os.remove(path_private)
        if os.path.isfile(path_public):
            os.remove(path_public)
        # SSHconfigファイルの指定Host設定削除
        if hostname in sshconf.Hosts:
            sshconf.DeleteHost(hostname)
    
    def __DeleteDatabase(self, account):
        path = Db().Paths['repo'].format(user=account['Username'])
        if os.path.isfile(path):
            os.remove(path)
        Db().Accounts['SshConfigures'].delete(AccountId=account['Id'])
        Db().Accounts['SshKeys'].delete(AccountId=account['Id'])
        Db().Accounts['TwoFactors'].delete(AccountId=account['Id'])
        Db().Accounts['AccessTokens'].delete(AccountId=account['Id'])
        Db().Accounts['Accounts'].delete(Id=account['Id'])

