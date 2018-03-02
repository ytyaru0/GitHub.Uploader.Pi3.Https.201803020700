#!python3
#encoding:utf-8
import os.path
import argparse
#import web.service.github.api.v3.AuthenticationsCreator
import web.service.github.api.v3.AuthenticationRouter
import web.service.github.api.v3.Client
from database.Database import Database as Db
import cui.uploader.Main
from web.log.Log import Log
from setting.Config import Config
import threading

class Main:
    def __init__(self):
        pass

    def Run(self):
        parser = argparse.ArgumentParser(
            description='GitHub Repository Uploader.',
        )
        parser.add_argument('path_dir_pj')
        parser.add_argument('-u', '--username')
        parser.add_argument('-d', '--description')
        parser.add_argument('-l', '--homepage', '--link', '--url')
        parser.add_argument('-m', '--messages', action='append')
        args = parser.parse_args()

        path_dir_db = Config()['Path']['Db']
        Log().Logger.debug(path_dir_db)
        
        # os.path.basename()で空文字を返されないための対策
        # https://docs.python.jp/3/library/os.path.html#os.path.basename
        if args.path_dir_pj.endswith('/'):
            args.path_dir_pj = args.path_dir_pj[:-1]
        
        if None is args.username:
            print(Config()['Github']['User'])
            args.username = Config()['Github']['User']
        
        if None is Db().Accounts['Accounts'].find_one(Username=args.username):
            Log().Logger.warning('指定したユーザ {0} はDBに存在しません。GitHubUserRegister.pyで登録してください。'.format(args.username))
            return
        
        # Contributionsバックアップ
        usernames = []
        if Config()['Github']['Contributions']['IsGet']:
            for a in Db().Accounts['Accounts'].find(): usernames.append(a['Username'])
            th = ContributionsThread(path_dir_db, usernames)
            th.start()
        
        # アップローダ起動
        #creator = web.service.github.api.v3.AuthenticationsCreator.AuthenticationsCreator(args.username)
        #authentications = creator.Create()
        #client = web.service.github.api.v3.Client.Client(authentications, args)
        #main = cui.uploader.Main.Main(client, args)
        #main.Run()
        client = web.service.github.api.v3.Client.Client(args.username, args)
        main = cui.uploader.Main.Main(client, args).Run()


class ContributionsThread(threading.Thread):
    def __init__(self, path_dir_db, usernames):
        threading.Thread.__init__(self)
        self.__path_dir_db = path_dir_db
        self.__usernames = usernames 
    def run(self):
        import batch.Contributions.Main
        m = batch.Contributions.Main.Main(self.__path_dir_db)
        for username in self.__usernames: m.Run(username)
        if Config()['Github']['Contributions']['IsMake']:
            self.__create_svg()
    def __create_svg(self):
        from batch.Contributions.SvgCreator import SvgCreator
        SvgCreator(Config()['Path']['Db']).Create()


if __name__ == '__main__':
    main = Main()
    main.Run()
