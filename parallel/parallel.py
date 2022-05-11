from joblib import Parallel, delayed
from properties.properties import theproperty
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
from logger.logger import logger



def palallelForEach(function, listofargs):
    res = Parallel(n_jobs=theproperty.thread, backend="threading")(delayed(function)(arg) for arg in listofargs)
    return res


def ParallelForEachShare(function, listofargs):
    res = Parallel(n_jobs=theproperty.thread, require='sharedmem', backend="threading")(delayed(function)(arg) for arg in listofargs)
    return res

class MyThreadPool:
    def __init__(self, threadnums, operators, maxops=0, opername=None, infosep=1000):
        self.operators = operators
        self.threadnums = threadnums
        self.pool = ThreadPoolExecutor(max_workers=threadnums)
        if maxops == 0:
            self.maxops = len(operators)
        else:
            self.maxops = maxops
        self.iterops = 0
        self.iterthread = 0
        self.threadlist = []
        self.opername = opername
        self.infosep = infosep

    def run(self, myfunc, **kwargs):
        for _ in range(min(self.threadnums, self.maxops)):
            self.threadlist.append(self.pool.submit(myfunc, self.operators[self.iterops], **kwargs))
            self.iterops += 1
        while self.iterops < self.maxops:
            for _ in range(self.threadnums):
                if self.iterops >= self.maxops:
                    break
                for _ in as_completed([self.threadlist[self.iterthread]]):
                    self.threadlist.append(self.pool.submit(myfunc, self.operators[self.iterops], **kwargs))
                    self.iterops += 1
                self.iterthread += 1
                if self.iterthread % self.infosep == 0:
                    logger.Info(
                        self.opername + " this is " + str(self.iterthread) + " / " + str(self.maxops) + " and time is " + str(datetime.datetime.now()))
        while self.iterthread < self.maxops:
            for _ in as_completed([self.threadlist[self.iterthread]]):
                self.iterthread += 1