import database.language.insert.LanguageSource
import database.language.insert.Inserter
class Main(object):
    def __init__(self, data, client):
        self.__data = data
        self.__client = client
        self.__source = database.language.insert.LanguageSource.LanguageSource()
        self.__inserter = database.language.insert.Inserter.Inserter(self.__data)
    def Run(self):
        self.__inserter.Insert(self.__source.Get())


if __name__ == "__main__":    
    m = Main()
    m.Run()

