class LionUndefined:
    
    def __init__(self):
        self.undefined = True

    def __bool__(self):
        return False
    
    __slots__ = ['undefined']
    