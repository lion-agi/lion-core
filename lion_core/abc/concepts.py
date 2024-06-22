from abc import ABC


## nouns
class Element(ABC):
    """represents a part of a space"""


class Ordering(ABC):
    """represents a structure of elements in a space"""
    

class Container(ABC):
    """represents a group of elements"""
    

class Event(ABC):
    """represents a change in a space"""


class Condition(ABC):
    """represents a state of a space"""


class Temporal(Element):
    """an element that can be referenced in time"""


class Record(Element):
    """a collection of elements"""



## adjectives
class Decidable(Element):
    ...
    
    
class Operable(Element):
    ...


class Relatable(Element):
    ...


class Sendable(Element):
    ...


