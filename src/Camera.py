from src.Vector3 import Vector3
from utils.Scene.sceneSchema import SceneData, CameraData, ObjectData
from src.Mesh import Mesh, load_mesh_from_obj
import sys

class Camera(object):
    def __init__(self, camera_data: CameraData):
        self.position: Vector3 = camera_data.lookfrom
        self.look_direction: Vector3 = camera_data.lookat
        self.screen_distance: float = camera_data.screen_distance
        self.screen_resolution: tuple[int, int] = (camera_data.image_width, camera_data.image_height)

        self.w = (self.look_direction - self.position).normalized()

        self.u: Vector3 = camera_data.up_vector.cross(self.w).normalized()
        self.v: Vector3 = self.w.cross(self.u).normalized()

        self._mirror_h = (self.u.x < 0)

    def plane_intersect(self, plane: ObjectData, ray_position: Vector3, ray_direction: Vector3):
        plane_point: Vector3 = plane.relative_pos
        plane_normal: Vector3 = plane.get_vetor("normal")
        if ray_direction.dot(plane_normal) == 0:
            return None
        t = (plane_point - ray_position).dot(plane_normal) / ray_direction.dot(plane_normal)
        if t < 0:
            return None
        return t

    def sphere_intersect(self, sphere: ObjectData, ray_position: Vector3, ray_direction: Vector3):
        sphere_center: Vector3 = sphere.relative_pos
        radius = sphere.get_num("radius")
        vetor_radius: Vector3 = ray_position - sphere_center
        a = ray_direction.dot(ray_direction)
        b = 2.0 * vetor_radius.dot(ray_direction)
        c = vetor_radius.dot(vetor_radius) - radius * radius
        delta = b * b - 4 * a * c
        if delta < 0:
            return None
        t = (-b - (delta) ** 0.5) / (2.0 * a)
        if t < 0:
            return None
        return t

    def mesh_intersect(self, mesh: Mesh, ray_position: Vector3, ray_direction: Vector3):
        """Möller-Trumbore. Retorna (t, normal_interpolada) ou None."""
        best_t = float('inf')
        best_normal = None
        for tri in mesh.triangles:
            v0 = mesh.vertices[tri[0]]
            v1 = mesh.vertices[tri[1]]
            v2 = mesh.vertices[tri[2]]
            edge1 = v1 - v0
            edge2 = v2 - v0
            h = ray_direction.cross(edge2)
            a = edge1.dot(h)
            if abs(a) < 1e-8:
                continue
            f = 1.0 / a
            s = ray_position - v0
            u = f * s.dot(h)
            if u < 0.0 or u > 1.0:
                continue
            q = s.cross(edge1)
            v = f * ray_direction.dot(q)
            if v < 0.0 or u + v > 1.0:
                continue
            t = f * edge2.dot(q)
            if t > 0.0001 and t < best_t:
                best_t = t
                n0 = mesh.vertex_normals[tri[0]]
                n1 = mesh.vertex_normals[tri[1]]
                n2 = mesh.vertex_normals[tri[2]]
                w = 1.0 - u - v
                best_normal = (n0 * w + n1 * u + n2 * v).normalized()
        if best_t == float('inf'):
            return None
        return best_t, best_normal

    def scene_intersect(self, scene: SceneData, ray_position: Vector3, ray_direction: Vector3):
        Object = None
        nearness = float('inf')
        for obj in scene.objects:
            t = None
            n = None
            if obj.obj_type == "plane":
                t = self.plane_intersect(obj, ray_position, ray_direction)
                if t is not None:
                    n = obj.get_vetor("normal")
            elif obj.obj_type == "sphere":
                t = self.sphere_intersect(obj, ray_position, ray_direction)
            elif obj.obj_type == "mesh":
                if not hasattr(obj, 'mesh') or obj.mesh is None:
                    continue
                result = self.mesh_intersect(obj.mesh, ray_position, ray_direction)
                if result is not None:
                    t, n = result
            if t is not None and t < nearness:
                nearness = t
                Object = obj
                Object._hit_normal = n
        return nearness, Object

    def trace_ray(self, scene: SceneData, ray_position: Vector3, ray_direction: Vector3):
        t, obj = self.scene_intersect(scene, ray_position, ray_direction)
        if obj:
            color = obj.material.color
            return Vector3(color.r * 255, color.g * 255, color.b * 255)
        return Vector3(0, 0, 0)

    def trace_image(self, scene: SceneData):
        for obj in scene.objects:
            if obj.obj_type == "mesh":
                try:
                    obj.mesh = load_mesh_from_obj(obj)
                except Exception as e:
                    print(f"Erro ao carregar malha {obj.get_property('path')}: {e}", file=sys.stderr)
                    obj.mesh = None

        with open("resultado.ppm", "w") as file:
            width = self.screen_resolution[0]
            height = self.screen_resolution[1]
            file.write(f"P3\n{width} {height}\n255\n")
            screen_position: Vector3 = self.position + self.w * self.screen_distance
            for y in range(height):
                for x in range(width):
                    u_cord = (x / (width - 1)) - 0.5
                    v_cord = (y / (height - 1)) - 0.5

                    if self._mirror_h:
                        u_cord = -u_cord

                    pixel_position: Vector3 = screen_position + u_cord * self.u + (-v_cord) * self.v
                    pixel_direction: Vector3 = (pixel_position - self.position).normalized()
                    color = self.trace_ray(scene, self.position, pixel_direction)
                    file.write(f"{int(color.x)} {int(color.y)} {int(color.z)}\n")