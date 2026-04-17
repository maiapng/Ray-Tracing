from src.Vector3 import Vector3
from src.Camera import Camera
import sys

def main():
    camera = Camera(Vector3(1,1,0), Vector3(50,3,2), 5, (160,120))
    camera.trace_image()

if __name__ == "__main__":
    main()