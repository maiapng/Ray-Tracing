from src.Vector3 import Vector3
from src.Camera import Camera

def main():
    camera = Camera(Vector3(1,1,0), Vector3(50,3,2), (320,240))
    print(camera)                

if __name__ == "__main__":
    main()