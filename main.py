import sys
from pathlib import Path
from time import time
from PIL import Image
from src.Camera import Camera
from utils.Scene.sceneParser import SceneJsonLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Escolhe a cena que servirá como input
scene_file = Path(__file__).parent / "utils" / "input" / "testScene.json" 

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
                for fb in fallbacks:
                    fb_path = (scene_dir / fb).resolve()
                    if fb_path.exists():
                        candidate = fb_path
                        break
            if candidate.exists():
                obj.other_properties["path"] = str(candidate)
            else:
                print(f"Aviso: não encontrei {rel_path} – malha ignorada.", file=sys.stderr)
                obj.other_properties["path"] = ""

    camera = Camera(scene.camera)
    camera.trace_image(scene)


    # Salva e mostra a imagem JPG
    im = Image.open("resultado.ppm")
    nm = str(int(time()))
    im.show()
    salvar = False
    if(salvar):
        Path("output").mkdir(exist_ok=True)
        im.save(f"output/{nm}.jpg")
    im.close()


if __name__ == "__main__":
    main()