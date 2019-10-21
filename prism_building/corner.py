import math

class Corner():


    def __init__(self, x=0, y=0 ):
        self.x = x
        self.y = y

    def __eq__(self,other_pt):
        return self.x == other_pt.x and self.y == other_pt.y

    def distance(self, pt_b):
        return math.sqrt((self.x - pt_b.x) ** 2 + (self.y - pt_b.y) ** 2)
