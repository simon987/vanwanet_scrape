import os
import re
import subprocess
from http.cookiejar import CookieJar

import requests
from bs4 import BeautifulSoup
from hexlib.web import cookie_from_string

with open(os.path.join(os.path.dirname(__file__), "aes.js"), "r") as f:
    AES = f.read()

SUB_PATTRN = re.compile(r'document\.cookie="(.+)";location.+$')


class Scraper:

    def __init__(self, domains: list, headers=None, proxies=None, logger=None):
        self._session = requests.session()
        self._domains = domains
        self._session.cookies = CookieJar()
        self.logger = logger

        if headers:
            self._session.headers = headers
        if proxies:
            self._session.proxies = proxies

    def _get(self, url, **kwargs):
        return self._session.get(url, **kwargs)

    def get(self, url, **kwargs):
        r = self._get(url, **kwargs)

        if Scraper._is_challenge_page(r):
            cookie_str = Scraper._execute_challenge(Scraper._transform_js(Scraper._get_js(r)))

            if self.logger:
                self.logger.debug("Executed challenge, got %s" % (cookie_from_string(cookie_str, ""),))

            for domain in self._domains:
                self._session.cookies.set_cookie(cookie_from_string(cookie_str, domain))

            return self.get(url, **kwargs)
        return r

    @staticmethod
    def _is_challenge_page(r):
        if r.text.startswith("<iframe ") and "VanwaNetDDoSMitigation=" in r.text:
            return True
        return False

    @staticmethod
    def _get_js(r):
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find("script", src=lambda x: not x).text

    @staticmethod
    def _transform_js(js):
        # Print cookie to console instead
        challenge = SUB_PATTRN.sub(r'res="\1";', js)
        return AES + challenge

    @staticmethod
    def _execute_challenge(js):
        js = js.replace("`", "")
        js = "let sb={};vm = require('vm');vm.runInNewContext(`" + js + "`, sb, {timeout: 3000});console.log(sb.res)"

        node = subprocess.Popen(
            ["node", "-e", js], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )
        result, stderr = node.communicate()

        if stderr != "":
            raise ValueError(stderr)

        return result
