AUTHORITIES = [("localhost", 6969)]

class Node:
    def __init__(self, authorities=AUTHORITIES) -> None:
        self.authorities = authorities


class NoNetworkError(Exception): pass

class Backlog(object):
    def __init__(self, node) -> None:
        self.node = node