import os, sys


class logger:
    @staticmethod
    def Log(msg: str):
        print(msg)

    @staticmethod
    def Info(msg: str):
        print(msg)

    @staticmethod
    def Error(msg: str, ex: Exception = None):
        print(msg)
        excetype, exceobj, excetb = sys.exc_info()
        fname = os.path.split(excetb.tb_frame.f_code.co_filename)[1]
        print(excetype, fname, excetb.tb_lineno)

    @staticmethod
    def Warnning(msg: str):
        print(f'Warnning : {msg}')
