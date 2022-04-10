from joblib import Parallel, delayed
from properties.properties import theproperty

def palallelForEach(function, listofargs):
    res = Parallel(n_jobs=theproperty.thread, backend="threading")(delayed(function)(arg) for arg in listofargs)
    return res


def ParallelForEachShare(function, listofargs):
    res = Parallel(n_jobs=theproperty.thread, require='sharedmem', backend="threading")(delayed(function)(arg) for arg in listofargs)
    return res