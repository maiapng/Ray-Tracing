from src.Vector3 import Vector3
from src.Camera import Camera
from utils.Scene.sceneParser import SceneJsonLoader
from pathlib import Path

scene_file = Path(__file__).parent / "utils" / "input" / "sampleScene.json"

def main():
    scene = SceneJsonLoader.load_file(str(scene_file))
    camera = Camera(scene.camera)
    camera.trace_image(scene)

if __name__ == "__main__":
    main()