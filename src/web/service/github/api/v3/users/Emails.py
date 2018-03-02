#!python3
#encoding:utf-8
import requests
import datetime
import time
import json
import web.http.Paginator
import web.service.github.api.v3.Response
from web.log.Log import Log
from web.service.github.uri.Endpoint import Endpoint

class Emails(object):
    def __init__(self, reqp, response):
        self.__reqp = reqp
        self.__response = response

    """
    メールアドレスを習得する。
    https://developer.github.com/v3/users/emails/#list-email-addresses-for-a-user
    @param {string} token。`user:email`権限をもったAccessTokenであること。
    """
    def Gets(self):
        method = 'GET'
        endpoint = 'user/emails'
        #params = self.__reqp.Get(method, endpoint)
        params = self.__auth.Route(method, endpoint).GetRequestParameters()
        Log().Logger.debug(params)
        paginator = web.http.Paginator.Paginator(web.service.github.api.v3.Response.Response())
        #url = 'https://api.github.com/user/emails'
        url = Endpoint(endpoint).ToUrl()
        return paginator.Paginate(url, **params)

