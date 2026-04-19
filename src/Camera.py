from src.Vector3 import Vector3
from utils.Scene.sceneSchema import SceneData, CameraData, ObjectData

class Camera(object):
    def __init__(self, camera_data:CameraData):
        self.position:Vector3 = camera_data.lookfrom
        self.look_direction:Vector3 = camera_data.lookat
        self.screen_distance:float = camera_data.screen_distance
        self.screen_resolution:tuple[int,int] = (camera_data.image_width, camera_data.image_height)

        self.w = (self.look_direction - self.position).normalized()
        self.v:Vector3 = camera_data.up_vector.normalized()
        self.u:Vector3 = self.w.cross(self.v).normalized()
         

    def plane_intersect(self, plane:ObjectData, ray_position:Vector3, ray_direction:Vector3):
        plane_point:Vector3 = plane.get_vetor("point_on_plane")
        plane_normal:Vector3 = plane.get_vetor("normal")
        if ray_direction.dot(plane_normal) == 0:
            #print("doesn't intersect")
            return None
        t = (plane_point - ray_position).dot(plane_normal) / ray_direction.dot(plane_normal)
        if t < 0:
            #print("INVERSE intersect")
            return None
        #print(t)
        return t

    def sphere_intersect(self, sphere:ObjectData, ray_position:Vector3, ray_direction:Vector3):
        sphere_center:Vector3 = sphere.get_vetor("center")
        radius = sphere.get_num("radius")

        vetor_radius:Vector3 = ray_position - sphere_center
        a = ray_direction.dot(ray_direction)
        b = 2.0 * vetor_radius.dot(ray_direction)
        c = vetor_radius.dot(vetor_radius) - radius * radius
        delta = b * b - 4 * a * c

        if delta < 0:
            return None
        t = (-b - (delta) ** 0.5) / (2.0 * a)

        if t < 0:
            #print("INVERSE intersect")
            return None
        return t

    def scene_intersect(self, scene:SceneData, ray_position:Vector3, ray_direction:Vector3):
        Object = None
        nearness   = float('inf')
        for obj in scene.objects:
            t = None
            if obj.obj_type == "plane":
               t = self.plane_intersect(obj, ray_position, ray_direction)
            elif obj.obj_type == "sphere":
                t = self.sphere_intersect(obj, ray_position, ray_direction)
            if t is not None and t < nearness:
                nearness = t
                Object = obj
        return nearness, Object

    def trace_ray(self, scene:SceneData, ray_position:Vector3, ray_direction:Vector3):
        t, obj = self.scene_intersect(scene, ray_position, ray_direction)
        if obj:
            color = obj.material.color
            return Vector3(color.r * 255, color.g * 255, color.b * 255)
        return Vector3(0, 0, 0)

    def trace_image(self, scene:SceneData):
        with open("resultado.ppm", "w") as file:
            width = self.screen_resolution[0]
            height = self.screen_resolution[1]
            file.write(f"P3\n{width} {height}\n255\n")
            screen_position:Vector3 = self.position + self.w*self.screen_distance
            for y in range(height):
                for x in range(width):  
                    u_cord = (x / (width - 1)) - 0.5
                    v_cord = (y / (height - 1)) - 0.5
                    pixel_position:Vector3 = screen_position + u_cord*self.u + (-v_cord)*self.v
                    pixel_direction:Vector3 = (pixel_position - self.position).normalized()
                    color = self.trace_ray(scene, self.position, pixel_direction)
                    file.write(f"{int(color.x)} {int(color.y)} {int(color.z)}\n")