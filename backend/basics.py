class BaseObject:
    def __init__(self, prog) -> None:
        self.prog = prog

    @classmethod
    def from_prog(cls, prog):
        return cls(prog)