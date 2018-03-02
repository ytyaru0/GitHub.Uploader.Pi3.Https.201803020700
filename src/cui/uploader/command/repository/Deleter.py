#!python3
#encoding:utf-8
import os.path
from web.log.Log import Log
from database.Database import Database as Db

class Deleter:
    def __init__(self, client, args):
        self.__client = client
        self.__args = args
        self.__userRepo = Db().Repositories[self.__args.username]
        self.__repo_name = os.path.basename(self.__args.path_dir_pj)

    def ShowDeleteRecords(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo_name)
        Log().Logger.info(repo)
        Log().Logger.info(self.__userRepo['Counts'].find_one(RepositoryId=repo['Id']))
        for record in self.__userRepo['Languages'].find(RepositoryId=repo['Id']):
            Log().Logger.info(record)

    def Delete(self):
        self.__DeleteLocalRepository()
        self.__client.Repositories.delete()
        self.__DeleteDb()

    def __DeleteLocalRepository(self):
        import shutil
        shutil.rmtree(os.path.join(self.__args.path_dir_pj, '.git'))

    def __DeleteDb(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo_name)
        self.__userRepo.begin()
        self.__userRepo['Languages'].delete(RepositoryId=repo['Id'])
        self.__userRepo['Counts'].delete(RepositoryId=repo['Id'])
        self.__userRepo['Repositories'].delete(Id=repo['Id'])
        self.__userRepo.commit()

