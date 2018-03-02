#!python3
#encoding:utf-8
import urllib.parse

class Endpoint:
    def __init__(self, endpoint):
        self.__endpoint = endpoint
        self.__keys = None

    @property
    def Keys(self):
        if self.__keys is None:
            self.__keys = []
            parsed = urllib.parse.urlparse(self.__endpoint)
            paths = parsed.path.split('/')
            for p in paths:
                if 0 == len(p): continue
                if ':' == p[0]: self.__keys.append(p[1:])
                # Github APIのサイトにあるAPI引数の説明文では、変化する引数を`:key`のように表記してある
                # https://developer.github.com/v3/repos/#list-user-repositories
                #   GET /users/:username/repos
                #   `:username`は変化する引数を指す。それをここではkeyと呼ぶ。
                # なお、HttpMethod(`GET`)やEndpoint(`/users/:username/repos`)の情報はGithub.Apis.sqlite3に保存する。
        return self.__keys

    def ToUrl(self, *args, **kwargs):
        url = urllib.parse.urljoin('https://api.github.com/', self.__endpoint)
        for key in kwargs:
            if key not in self.Keys: raise Endpoint.NotHasKeyException(self.__endpoint, key)
            url = url.replace(':'+key, str(kwargs[key]))
        return url

    class NotHasKeyException(Exception):
        def __init__(self, endpoint, key):
            super().__init__('API Endpoint に必要な引数 {1} がありません。{1}キーとその値をセットしたdictを用意してください。: {0}'.format(endpoint, key))


if __name__ == '__main__':
    username = 'TestUserName'
    e = Endpoint('/users/:username/repos')
    print(e.Keys)
    print(e.ToUrl(username=username))
    assert('https://api.github.com/users/{0}/repos'.format(username) == e.ToUrl(username=username))
    #print(e.ToUrl(not_found_key='TestUserName'))

    e = Endpoint('ABC/:username/repos')
    print(e.Keys)
    print(e.ToUrl(username=username))
    assert('https://api.github.com/ABC/{0}/repos'.format(username) == e.ToUrl(username=username))
    #print(e.ToUrl(not_found_key='TestUserName'))

    username = 'TestUserName'
    e = Endpoint('some/:id/hoge/:username')
    print(e.Keys)
    
    print(e.ToUrl(id=100, username=username))
    #print(e.ToUrl(**{'id': 100, 'username': username}))
    assert('https://api.github.com/some/{0}/hoge/{1}'.format(100, username) == e.ToUrl(id=100, username=username))
    #print(e.ToUrl(not_found_key='TestUserName'))

