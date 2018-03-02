#!python3
#encoding:utf-8
from datetime import datetime
from web.log.Log import Log
from database.Database import Database as Db

class Aggregate:
    def __init__(self, args):
        self.__args = args
        self.__first_date = None
        self.__last_date = None
        self.__date_span = None
        self.__date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.__sum_repo_count = 0
        self.__sum_code_size = 0
        self.__repoDb = Db().Repositories[self.__args.username]
        
    def Show(self):
        self.__calc_date()
        Log().Logger.info(("開始日: {0:%s}" % (self.__date_format)).format(self.__first_date))
        Log().Logger.info(("最終日: {0:%s}" % (self.__date_format)).format(self.__last_date))
        Log().Logger.info("期  間: {0} 日間".format(self.__date_span))
        self.__sum_repo_count = self.__repoDb['Repositories'].count()
        Log().Logger.info("リポジトリ総数  : {0}".format(self.__sum_repo_count))
        Log().Logger.info("リポジトリ平均数: {0} repo/日".format(self.__sum_repo_count / self.__date_span))
        self.__sum_code_size = self.__repoDb.query("select SUM(Size) SumSize from Languages;").next()['SumSize']
        Log().Logger.info("コード平均量    : {0} Byte/日".format(self.__sum_code_size / self.__date_span))
        Log().Logger.info("コード総量      : {0} Byte".format(self.__sum_code_size))
        self.__show_sizes_by_languages()

    def __calc_date(self):
        first_date = self.__repoDb.query("select min(CreatedAt) FirstDate from Repositories;").next()['FirstDate']
        last_date = self.__repoDb.query("select max(CreatedAt) LastDate from Repositories;").next()['LastDate']
        self.__first_date = datetime.strptime(first_date, self.__date_format)
        self.__last_date = datetime.strptime(last_date, self.__date_format)
        self.__date_span = (self.__last_date - self.__first_date).days
        if 0 == self.__date_span:
            self.__date_span = 1

    def __show_sizes_by_languages(self):
        # 桁あわせ：最も長い言語名を取得する
        name_length = 0
        for res in self.__repoDb.query('select * from Languages where length(Language)=(select max(length(Language)) from Languages)'):
            name_length = res['Language']
        # 桁あわせ：最も大きい言語別合計Byteを取得する
        size_length = self.__repoDb.query('select sum(Size) SumSize from Languages group by Language order by SumSize desc').next()['SumSize']
        # 言語別の合計Byte数
        format_str = "  {0:<%d}: {1:>%d} Byte" % (len(name_length), len(str(size_length)))
        for lang in self.__repoDb.query('select Language, sum(Size) SumSize from Languages group by Language order by SumSize desc'):
            Log().Logger.info(format_str.format(lang['Language'], lang['SumSize']))

