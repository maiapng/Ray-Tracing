from src.Vector3 import Vector3
from utils.Scene.sceneSchema import CameraData

class Camera(object):
    def __init__(self, camera_data:CameraData):
        self.position:Vector3 = camera_data.lookfrom
        self.look_dir:Vector3 = camera_data.lookat
        self.screen_distance:float = camera_data.screen_distance
        self.screen_resolution:tuple[int,int] = (camera_data.image_width, camera_data.image_height)

        self.w:Vector3 = self.look_dir.normalized()
        self.u:Vector3 = camera_data.up_vector.normalized()
        self.v:Vector3 = self.w.cross(self.u).normalized()

    def trace_ray(self, scene, pixel_dir:Vector3):
        pass

    def trace_image(self, scene=None):
        screen_position:Vector3 = self.position + self.w*self.screen_distance 
        for x in range(-self.screen_resolution[0], self.screen_resolution[0]):
            for y in range(-self.screen_resolution[1], self.screen_resolution[1]):
                pixel_position:Vector3 = screen_position + x*self.u + y*self.v
                pixel_dir:Vector3 = (pixel_position - self.position).normalized()
                print(f"({x},{y}): {pixel_dir}")
                self.trace_ray(scene, pixel_dir)