from src.Vector3 import Vector3
import math

def main():
    p = Vector3(0,0,0)
    v = Vector3(2,3,7)
    l = Vector3(1,0,0) * 100
    k = Vector3(1,1,0) * 100

    print(math.degrees(l.angle_to(k)))
    print(l.cross(k))
    print(l.dot(k))
if __name__ == "__main__":
    main()