from src.Vector3 import Vector3
from utils.Scene.sceneSchema import SceneData, CameraData, ObjectData
from src.Mesh import Mesh, load_mesh_from_obj
import sys
import os
import multiprocessing as mp

state = {}

def init_worker(position, u, v, screen_position, width, height, scene):
    state['position'] = position
    state['u'] = u
    state['v'] = v
    state['screen_position'] = screen_position
    state['width'] = width
    state['height'] = height
    state['scene'] = scene

def plane_intersect_fn(plane, ray_position, ray_direction):
    plane_point = plane.relative_pos
    plane_normal = plane.get_vetor("normal")
    if ray_direction.dot(plane_normal) == 0:
        return None
    t = (plane_point - ray_position).dot(plane_normal) / ray_direction.dot(plane_normal)
    if t < 0:
        return None
    return t

def sphere_intersect_fn(sphere, ray_position, ray_direction):
    sphere_center = sphere.relative_pos
    radius = sphere.get_num("radius")
    vetor_radius = ray_position - sphere_center
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

def mesh_intersect_fn(mesh, ray_position, ray_direction):
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

def scene_intersect_fn(scene, ray_position, ray_direction):
    Object = None
    hit_normal = None
    hit_material = None
    nearness = float('inf')
    for obj in scene.objects:
        if obj.obj_type == "plane":
            t = plane_intersect_fn(obj, ray_position, ray_direction)
            if t is not None and t < nearness:
                nearness = t
                Object = obj
                hit_normal = obj.get_vetor("normal").normalized()
                hit_material = obj.material
        elif obj.obj_type == "sphere":
            t = sphere_intersect_fn(obj, ray_position, ray_direction)
            if t is not None and t < nearness:
                nearness = t
                Object = obj
                hit_point = ray_position + ray_direction * t
                hit_normal = (hit_point - obj.relative_pos).normalized()
                hit_material = obj.material
        elif obj.obj_type == "mesh":
            if not hasattr(obj, 'mesh') or obj.mesh is None:
                continue
            result = mesh_intersect_fn(obj.mesh, ray_position, ray_direction)
            if result is not None:
                t, n = result
                if t < nearness:
                    nearness = t
                    Object = obj
                    hit_normal = n
                    hit_material = obj.material
    return nearness, Object, hit_normal, hit_material

def trace_row_worker(y):
    position = state['position']
    u = state['u']
    v = state['v']
    screen_position = state['screen_position']
    width = state['width']
    height = state['height']
    scene = state['scene']
    row = []
    for x in range(width):
        u_cord = (x / (width - 1)) - 0.5
        v_cord = (y / (height - 1)) - 0.5
        pixel_position = screen_position + u_cord * u + (-v_cord) * v
        pixel_direction = (pixel_position - position).normalized()
        _, obj, _, mat = scene_intersect_fn(scene, position, pixel_direction)
        if obj:
            row.append(Vector3(mat.color.r * 255, mat.color.g * 255, mat.color.b * 255))
        else:
            row.append(Vector3(0, 0, 0))
    return y, row


class Camera(object):
    def __init__(self, camera_data: CameraData):
        self.position: Vector3 = camera_data.lookfrom
        self.look_direction: Vector3 = camera_data.lookat
        self.screen_distance: float = camera_data.screen_distance
        self.screen_resolution: tuple[int, int] = (camera_data.image_width, camera_data.image_height)

        self.w = (self.look_direction - self.position).normalized()
        self.u: Vector3 = self.w.cross(camera_data.up_vector).normalized()
        self.v: Vector3 = self.u.cross(self.w).normalized()

    def plane_intersect(self, plane, ray_position, ray_direction):
        return plane_intersect_fn(plane, ray_position, ray_direction)

    def sphere_intersect(self, sphere, ray_position, ray_direction):
        return sphere_intersect_fn(sphere, ray_position, ray_direction)

    def mesh_intersect(self, mesh, ray_position, ray_direction):
        return mesh_intersect_fn(mesh, ray_position, ray_direction)

    def scene_intersect(self, scene, ray_position, ray_direction):
        return scene_intersect_fn(scene, ray_position, ray_direction)

    def trace_ray(self, scene, ray_position, ray_direction):
        _, obj, _, mat = scene_intersect_fn(scene, ray_position, ray_direction)
        if obj:
            return Vector3(mat.color.r * 255, mat.color.g * 255, mat.color.b * 255)
        return Vector3(0, 0, 0)

    def trace_image(self, scene: SceneData):
        for obj in scene.objects:
            if obj.obj_type == "mesh":
                try:
                    obj.mesh = load_mesh_from_obj(obj)
                except Exception as e:
                    print(f"Erro ao carregar malha {obj.get_property('path')}: {e}", file=sys.stderr)
                    obj.mesh = None

        width = self.screen_resolution[0]
        height = self.screen_resolution[1]
        screen_position: Vector3 = self.position + self.w * self.screen_distance
        pixels = [None] * height

        num_workers = os.cpu_count() or 4
        init_args = (self.position, self.u, self.v, screen_position, width, height, scene)
        chunksize = max(1, height // (num_workers * 4))
        with mp.Pool(processes=num_workers, initializer=init_worker, initargs=init_args) as pool:
            for y, row in pool.imap_unordered(trace_row_worker, range(height), chunksize=chunksize):
                pixels[y] = row

        print(f"P3\n{width} {height}\n255")
        for y in range(height):
            for color in pixels[y]:
                print(f"{int(color.x)} {int(color.y)} {int(color.z)}")