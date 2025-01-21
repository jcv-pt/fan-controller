from .fault import Fault

class Failures:

    def __init__(self):
        self.__collection = {}

    def report(self, faultId: str):
        if not self.exists(faultId):
            self.__collection[faultId] = Fault(faultId)

    def getFault(self, faultId: str):
        if self.exists(faultId):
            return self.__collection[faultId]
        else:
            return None

    def exists(self, faultId: str):
        return faultId in self.__collection

    def clear(self, faultId: str):
        self.__collection.pop(faultId)