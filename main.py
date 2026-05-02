import sys
from pathlib import Path
from time import time
from PIL import Image
from src.Camera import Camera
from utils.Scene.sceneParser import SceneJsonLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))

scene_file = Path(__file__).parent / "utils" / "input" / "sampleScene.json"

def main():
    scene = SceneJsonLoader.load_file(str(scene_file))
    scene_dir = scene_file.parent.absolute()

    for obj in scene.objects:
        if obj.obj_type == "mesh":
            rel_path = obj.get_property("path")
            candidate = (scene_dir / rel_path).resolve()

            if not candidate.exists():
                candidate = (scene_dir / Path(rel_path).name).resolve()

            if not candidate.exists():
                fallbacks = ["cubo.obj", "monkey.obj", "cuboTransparent.obj"]
                found = False
                for fb in fallbacks:
                    fb_path = (scene_dir / fb).resolve()
                    if fb_path.exists():
                        candidate = fb_path
                        found = True
                        break
                if not found:
                    print(f"Aviso: arquivo não encontrado para '{rel_path}' – malha ignorada.",
                          file=sys.stderr)
                    obj.other_properties["path"] = ""
                    continue

            obj.other_properties["path"] = str(candidate)

    camera = Camera(scene.camera)
    camera.trace_image(scene)

    im = Image.open("resultado.ppm")
    im.show()
    nm = str(int(time()))
    im.save(f"renders/{nm}.jpg")

if __name__ == "__main__":
    main()