from src.Vector3 import Vector3
from utils.Scene.sceneSchema import SceneData, CameraData, ObjectData

class Camera(object):
    def __init__(self, camera_data:CameraData):
        self.position:Vector3 = camera_data.lookfrom
        self.look_direction:Vector3 = camera_data.lookat
        self.screen_distance:float = camera_data.screen_distance
        self.screen_resolution:tuple[int,int] = (camera_data.image_width, camera_data.image_height)

        self.w:Vector3 = self.look_direction.normalized()
        self.u:Vector3 = camera_data.up_vector.normalized()
        self.v:Vector3 = self.w.cross(self.u).normalized()

    def plane_intersect(self, plane:ObjectData, ray_position:Vector3, ray_direction:Vector3):
        plane_point:Vector3 = plane.get_vetor("point_on_plane")
        plane_normal:Vector3 = plane.get_vetor("point_on_plane")
        if ray_direction.dot(plane_normal) == 0:
            print("doesn't intersect")
            return
        t = (plane_point - ray_position) * plane_normal / ray_direction.dot(plane_normal)
        print(t)

    def scene_intersect(self, scene:SceneData, ray_position:Vector3, ray_direction:Vector3):
        for obj in scene.objects:
            if obj.obj_type == "plane":
                self.plane_intersect(obj, ray_position, ray_direction)

    def trace_ray(self, scene:SceneData, ray_position:Vector3, ray_direction:Vector3):
        self.scene_intersect(scene, ray_position ,ray_direction)

    def trace_image(self, scene:SceneData):
        for i in scene.objects: print(i)
        screen_position:Vector3 = self.position + self.w*self.screen_distance 
        for x in range(-self.screen_resolution[0], self.screen_resolution[0]):
            for y in range(-self.screen_resolution[1], self.screen_resolution[1]):
                pixel_position:Vector3 = screen_position + x*self.u + y*self.v
                pixel_direction:Vector3 = (pixel_position - self.position).normalized()
                self.trace_ray(scene, self.position, pixel_direction)
                break