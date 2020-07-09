import sqlite3

from .cars import Controller


class Database():

    def __init__(self, url):
        self.url = url
        self.conn = sqlite3.connect(url)
        self.controller = Controller(self.conn)


    def close(self):
        self.url = None
        self.conn.close()
        self.controller.close()
        self.controller = None