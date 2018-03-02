import pathlib
import yaml
#import PyYAML

class YamlMeta(type):
    __instance = None
    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance.Yaml
    
    @classmethod
    def __Load(cls):
        path = pathlib.Path('../res/config.yml').resolve()
        print(path)
        with path.open() as f:
            setattr(cls.__instance, '_{}__{}'.format(cls.__name__, 'yaml'), yaml.load(f))

