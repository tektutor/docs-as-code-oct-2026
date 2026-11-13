"""Small client for the Codebeamer REST API v3.

Settings come from environment variables, never from the code:
    CB_URL       for example https://trial.codebeamer.com/api/v3
                 or http://localhost:8090/api/v3 for the practice server
    CB_TOKEN     an API token (sent as a Bearer token), or
    CB_USER and CB_PASSWORD for Basic authentication
"""
import os
import sys

import requests


class CodebeamerError(Exception):
    pass


class Codebeamer:
    def __init__(self, url=None, user=None, password=None, token=None, timeout=30):
        self.url = (url or os.environ.get("CB_URL", "")).rstrip("/")
        if not self.url:
            raise CodebeamerError("Set CB_URL, for example http://localhost:8090/api/v3")
        self.session = requests.Session()
        token = token or os.environ.get("CB_TOKEN")
        if token:
            self.session.headers["Authorization"] = "Bearer " + token
        else:
            self.session.auth = (user or os.environ.get("CB_USER", ""),
                                 password or os.environ.get("CB_PASSWORD", ""))
        self.session.headers["Accept"] = "application/json"
        self.timeout = timeout

    def call(self, method, path, body=None, params=None):
        r = self.session.request(method, self.url + path, json=body, params=params,
                                 timeout=self.timeout)
        if r.status_code >= 400:
            raise CodebeamerError("%s %s -> HTTP %s: %s" % (method, path, r.status_code, r.text[:200]))
        return r.json() if r.content else {}

    def get(self, path, **params):
        return self.call("GET", path, params=params or None)

    def post(self, path, body):
        return self.call("POST", path, body=body)

    def put(self, path, body):
        return self.call("PUT", path, body=body)

    def query(self, cbql, page_size=100):
        """All items that match a cbQL query, page by page."""
        page, items = 1, []
        while True:
            r = self.get("/items/query", queryString=cbql, page=page, pageSize=page_size)
            items += r.get("items", [])
            if len(items) >= r.get("total", 0) or not r.get("items"):
                return items
            page += 1


if __name__ == "__main__":
    cb = Codebeamer()
    for p in cb.get("/projects"):
        print(p["id"], p["name"])
    sys.exit(0)
