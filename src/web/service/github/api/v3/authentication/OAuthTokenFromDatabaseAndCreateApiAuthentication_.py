#!python3
#encoding:utf-8
import traceback
from web.service.github.api.v3.authentication.OAuthTokenFromDatabaseAuthentication import OAuthTokenFromDatabaseAuthentication
import pyotp
import dataset
from database.Database import Database as Db

class OAuthTokenFromDatabaseAndCreateApiAuthentication(OAuthTokenFromDatabaseAuthentication):
    def __init__(self, username, password, two_factor_secret=None, scopes=None):
#    def __init__(self, db, username, password, two_factor_secret=None):
#        self.__db = db
        self.__username = username
        self.__password = password
        self.__two_factor_secret = two_factor_secret
        try:
            #super().__init__(self.__db, self.__username)
            super().__init__(self.__username, scopes=None)
        except:
            traceback.print_exc()
            self.__token = self.__CreateToken(scopes)
    
    def SetAccessToken(self, scopes=None):
        try:
            self.__token = super().SetAccessToken(scopes)
        except:
            # APIで新しいTokenを生成する。次回から使いまわせるようDBに保存する。
            traceback.print_exc()
            self.__token = self.__CreateToken(scopes)

    def __CreateToken(scopes):
        account = Db().Accounts['Accounts'].find_one(Username=self.__username)
        if None is account:
            raise Exception('指定ユーザ {user} はDB未登録です。登録してください。')
            Db().Accounts['Accounts'].insert(self.__CreateRecordAccount())

        twofactor = Db().Accounts['TwoFactors'].find_one(AccountId=account['Id'])
        if twofactor is None:
        else:
            """
            # 再帰呼出になる！
            from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
            auth = TwoFactorAuthentication(self.__username, account['Passowrd'], twofactor['Secret'])

            from web.service.github.api.v3.Client import Client
            j = Client().Authorizations.Create(scopes=scopes)
            Db().Accounts['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], j))
            return j['token']
            """

            """
            api = web.service.github.api.v3.Authorizations(self.__username, self.__password)
            j = api.Create(scopes=scopes)
            #j = api.Create(otp=self.__totp.now(), scopes=scopes)
            Db().Accounts['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], j))
            return j['token']
            """
        otp = None
        if None is not self.__two_factor_secret:
            self.__totp = pyotp.TOTP(self.__two_factor_secret)
            otp = self.__totp.now()
        api = web.service.github.api.v3.Authorizations(self.__username, self.__password)
        j = api.Create(otp=self.__totp.now(), scopes=scopes)
        Db().Accounts['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], j))
        return j['token']
        
    def __CreateRecordToken(self, account_id, j):
        return dict(
            AccountId=account_id,
            IdOnGitHub=j['id'],
            Note=j['note'],
            AccessToken=j['token'],
            Scopes=self.__ArrayToString(j['scopes']),
            SshKeyId=ssh_key_id
        )

    """
    requestsライブラリのAPIで使うheadersを生成する。
    """
    def GetHeaders(self):
        return super().GetHeaders()

    """
    requestsライブラリのAPIで使う**kwargsを生成する。
    requests.get(url, **this.GetRequestParameters())
    """
    def GetRequestParameters(self):
        return super().GetRequestParameters()

    def __ArrayToString(self, array):
        if None is array or 0 == len(array):
            return None
        ret = ""
        for v in array:
            ret += v + ','
            print(ret)
        print(ret[:-1])
        return ret[:-1]

