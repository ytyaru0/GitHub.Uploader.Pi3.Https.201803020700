import pathlib
from setting.YamlMeta import YamlMeta
import yaml
class Config(metaclass=YamlMeta):
    def __init__(self):
        self.__Load()
        self.__SetValues()

    @property
    def Yaml(self): return self.__yaml

    def __Load(self):
        path_dir_root = pathlib.Path(__file__).parent.parent.parent
        path_file_config = path_dir_root / 'res' / 'config.yml'
        path = path_file_config.resolve()
        with path.open() as f:
            self.__yaml = yaml.load(f)
            print(self.__yaml)

    def __SetValues(self):
        self.Yaml['Path']['Db']
        self.__SetPathDb()
        self.__SetGitRemote()

    def __SetPathDb(self):
        if '' == self.__yaml['Path']['Db']: self.__yaml['Path']['Db'] = './res/db/'
        if not pathlib.PurePath(self.__yaml['Path']['Db']).is_absolute():
            path_dir_root = pathlib.PurePath(__file__).parent.parent.parent
            self.__yaml['Path']['Db'] = pathlib.Path(path_dir_root, self.__yaml['Path']['Db'])
            self.__yaml['Path']['Db'].mkdir(parents=True, exist_ok=True)

    def __SetGitRemote(self):
        from web.service.github.uri import Protocol
        class_name = self.__yaml['Git']['Remote'][0].upper() + self.__yaml['Git']['Remote'][1:].lower()
        protocol_class = getattr(Protocol, class_name)
        self.__yaml['Git']['Remote'] = protocol_class()

