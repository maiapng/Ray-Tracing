from math import sqrt, atan2

class Vector3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other:Vector3):
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other:Vector3):
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __mul__(self, other:int|float):
        return Vector3(
            self.x * other,
            self.y * other,
            self.z * other
        )
    
    def __rmul__(self, other:int|float):
        return Vector3(
            self.x * other,
            self.y * other,
            self.z * other
        )

    def __truediv__(self, other:int|float):
        return Vector3(
            self.x / other,
            self.y / other,
            self.z / other
        )

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def abs(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z))

    def dot(self, other:Vector3):
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def cross(self, other:Vector3):
        return Vector3(
            (self.y * other.z) - (self.z * other.y),
            (self.z * other.x) - (self.x * other.z),
            (self.x * other.y) - (self.y * other.x)
        )
    
    def angle_to(self, other:Vector3):
        return atan2(self.cross(other).length(), self.dot(  other))

    def length_squared(self):
        return self.x**2 + self.y**2 + self.z**2
    
    def length(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalized(self):
        length_squared = self.x**2 + self.y**2 + self.z**2
        if length_squared == 0:
            return Vector3(0,0,0)
        length = sqrt(length_squared)
        self.x /= length
        self.y /= length
        self.z /= length
        return self

    def direction_to(self, to:Vector3):
        return (to - self).normalized()
    
    def distance_squared_to(self, to:Vector3):
        return (to.x - self.x)**2 + (to.y - self.y)**2 + (to.z - self.z)**2

    def distance_to(self, to:Vector3):
        return sqrt((to.x - self.x)**2 + (to.y - self.y)**2 + (to.z - self.z)**2)

    def get_any_perpendicular(self):
        return self.cross(Vector3(1,0,0) if (abs(self.x) <= abs(self.y) and abs(self.x) <= abs(self.z)) else Vector3(0,1,0)).normalized();