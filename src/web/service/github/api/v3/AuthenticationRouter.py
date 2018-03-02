#!python3
#encoding:utf-8
from database.Database import Database as Db
from web.service.github.api.v3.authentication.Authentication import Authentication
from web.service.github.api.v3.authentication.NonAuthentication import NonAuthentication
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
from web.service.github.api.v3.authentication.OAuthTokenFromDatabaseAuthentication import OAuthTokenFromDatabaseAuthentication
#from web.service.github.api.v3.authentication.OAuthTokenFromDatabaseAndCreateApiAuthentication import OAuthTokenFromDatabaseAndCreateApiAuthentication

class AuthenticationRouter:
#class AuthenticationsCreator(object):
    def __init__(self, username=None):
        self.__username = username

    #def Create(self, http_method, endpoint, username=None, scopes=None):
    def Route(self, http_method, endpoint, username=None):
        if None is username: username = self.__username
        account = Db().Accounts['Accounts'].find_one(Username=username)

        api = Db().Apis['Apis'].find_one(HttpMethod=http_method.upper(), Endpoint=endpoint)
        grants = [g.strip() for g in api['Grants'].split(",")]
        if None is api or None is api['AuthMethods'] or '' == api['AuthMethods'].strip():
            if None is username: return NonAuthentication()
            else: return self.__GetTokenAuth(account, grants)
            #else: return OAuthAuthentication(account['AccessToken'])
        else:
            if None is username: raise Exception('指定したユーザ {0} はDBに未登録です。登録してから実行してください。'.format(username))
            if "Token" in api['AuthMethods']: return self.__GetTokenAuth(account, grants)
            elif "Basic" in api['AuthMethods']: return self.__GetBasicAuth(account)
            elif "ClientId" in api['AuthMethods']:
                raise NotImplementedError('ClientId認証は未実装です。Not implemented clientId authorization.')
            else:
                raise NotImplementedError('ApiDBに登録された次の認証方法は未実装です。: {0} {1} {2}'.format(api['HttpMethod'], api['Endpoint'], api['AuthMethods']))

    def __GetBasicAuth(self, account):
        twofactor = Db().Accounts['TwoFactors'].find_one(AccountId=account['Id'])
        if twofactor is None: return BasicAuthentication(account['Username'], account['Password'])
        else: return TwoFactorAuthentication(account['Username'], account['Password'], twofactor['Secret'])
        
    def __GetTokenAuth(self, account):
        try: return OAuthTokenFromDatabaseAuthentication(account['Username'], grants)
        except NotHasGrantsException as e:
            # 指定のscopeを持ったTokenを作成する（あるいは既存のTokenに権限追加しほうが？）
            basicAuth = self.__GetBasicAuth(account)
            from web.service.github.api.v3.Client import Client
            j = Client().Authorizations.Create(scopes=scopes)
            # DBに登録する
            Db().Accounts['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], j))
            return OAuthTokenFromDatabaseAuthentication(account['Username'], grants)
        
    def __CreateRecordToken(self, account_id, j):
        return dict(
            AccountId=account_id,
            IdOnGitHub=j['id'],
            Note=j['note'],
            AccessToken=j['token'],
            Scopes=self.__ArrayToString(j['scopes']),
            SshKeyId=None #  ※SSH鍵作成したときは設定すべき。このToken削除されるとSSH公開鍵も削除されてしまう！
            #SshKeyId=ssh_key_id
        )

