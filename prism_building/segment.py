import math


class Segment():

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def length(self):
        return math.sqrt((self.start.x - self.end.x) ** 2 + (self.start.y - self.end.y) ** 2)

    def is_point_on_segment(self, pt):
        return math.isclose(self.start.distance(pt) + self.end.distance(pt), self.start.distance(self.end))

    def __eq__(self, other_segment):
        return (self.start == other_segment.start and self.end == other_segment.end) or (
                    self.start == other_segment.end and self.end == other_segment.start)
