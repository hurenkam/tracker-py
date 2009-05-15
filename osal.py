class Osal:
    instance = None

    def GetInstance():
        return Osal.instance

    def ShowInfo(self,text):
        pass

    def ShowError(self,text):
        pass

    def Sleep(self,s):
        pass

    def GetTime(self):
        pass

    def GetIsoTime(self):
        pass

    GetInstance = staticmethod(GetInstance)

if __name__ == '__main__':
    pass
