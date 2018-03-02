#!python3
#encoding:utf-8
import sys
import os.path
import argparse

class Main:
    def __init__(self):
        self.__path_dir_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    def Run(self):
        parser = argparse.ArgumentParser(
            description='GitHub User Resist CUI.',
        )
        sub_parser = parser.add_subparsers()

        # insertサブコマンド
        parser_insert = sub_parser.add_parser('insert', help='see `insert -h`')
        parser_insert.add_argument('-u', '--username', '--user', required=True)
        parser_insert.add_argument('-p', '--password', '--pass', required=True)
        parser_insert.add_argument('-s', '--ssh-host', '--ssh')
        parser_insert.add_argument('-t', '--two-factor-secret-key', '--two')
        parser_insert.add_argument('-r', '--two-factor-recovery-code-file-path', '--recovery')
        parser_insert.add_argument('-a', '--auto', action='store_const', const=True, default=False)
        parser_insert.set_defaults(handler=self.__insert)

        # updateサブコマンド
        parser_update = sub_parser.add_parser('update', help='see `update -h`')
        parser_update.add_argument('-u', '--username', '--user', required=True)
        parser_update.add_argument('-rn', '--rename')
        parser_update.add_argument('-p', '--password', '--pass')
        parser_update.add_argument('-m', '--mailaddress', '--mail', action='store_const', const=True, default=False)
        parser_update.add_argument('-s', '--ssh-host', '--ssh')
        parser_update.add_argument('-t', '--two-factor-secret-key', '--two')
        parser_update.add_argument('-r', '--two-factor-recovery-code-file-path', '--recovery')
        parser_update.add_argument('-a', '--auto', action='store_const', const=True, default=False)
        parser_update.set_defaults(handler=self.__update)

        # deleteサブコマンド
        parser_delete = sub_parser.add_parser('delete', help='see `delete -h`')
        parser_delete.add_argument('-u', '--username', '--user', required=True)
        parser_delete.add_argument('-a', '--auto', action='store_const', const=True, default=False)
        parser_delete.set_defaults(handler=self.__delete)
        
        # コマンドライン引数をパースして対応するハンドラ関数を実行
        args = parser.parse_args()
        if hasattr(args, 'handler'):
            args.handler(args)
        else:
            # 未知のサブコマンドの場合はヘルプを表示
            parser.print_help()

    def __insert(self, args):
        import cui.register.command.Inserter
        inserter = cui.register.command.Inserter.Inserter(self.__path_dir_root)
        return inserter.Run(args)

    def __delete(self, args):
        import cui.register.command.Deleter
        deleter = cui.register.command.Deleter.Deleter(self.__path_dir_root)
        deleter.Run(args)

    def __update(self, args):
        import cui.register.command.Updater
        updater = cui.register.command.Updater.Updater(self.__path_dir_root)
        return updater.Run(args)


if __name__ == '__main__':
    main = Main()
    main.Run()
