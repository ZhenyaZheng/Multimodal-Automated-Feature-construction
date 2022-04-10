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

        excetype, exceobj, excetb = sys.exc_info()
        fname = os.path.split(excetb.tb_frame.f_code.co_filename)[1]
        print(excetype, fname, excetb.tb_lineno)
        print(msg)
        raise (ex)

    @staticmethod
    def Warnning(msg: str):
        print(f'Warnning : {msg}')
