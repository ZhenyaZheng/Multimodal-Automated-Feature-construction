from MAFC_Operator.ColumnInfo import ColumnInfo
from MAFC_Operator.Operators import Operators


class RankFilter:
    def __init__(self):
        pass

    def rankAndFilter(self, operatorslist: list[Operators], previousiterchosenatts: list[ColumnInfo] = None):
        operatorslist.sort(key=lambda ob: ob.getFScore(), reverse=True)
        return operatorslist
