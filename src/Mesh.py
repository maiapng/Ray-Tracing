# Mesh.py
import math
from pathlib import Path
from src.Vector3 import Vector3
from src.Mat4 import Mat4
from utils.MeshReader.ObjReader import ObjReader

class Mesh:
    def __init__(self, vertices, triangles, vertex_normals, diffuse_color):
        self.vertices = vertices
        self.triangles = triangles
        self.vertex_normals = vertex_normals
        self.diffuse_color = diffuse_color

def load_mesh_from_obj(obj_data):
    obj_path_str = obj_data.get_property("path")
    if not obj_path_str:
        return None
    obj_path = Path(obj_path_str)

    reader = ObjReader(str(obj_path))
    local_vertices = [Vector3(p.x, p.y, p.z) for p in reader.get_vertices()]
    faces_data = reader.get_faces()

    triangles = []
    for face in faces_data:
        if len(face.vertice_indice) >= 3:
            i0, i1, i2 = face.vertice_indice[0:3]
            triangles.append((i0, i1, i2))

    vertex_normals = [Vector3(0, 0, 0) for _ in range(len(local_vertices))]
    
    for (i0, i1, i2) in triangles:
        v0, v1, v2 = local_vertices[i0], local_vertices[i1], local_vertices[i2]
        edge1 = v1 - v0
        edge2 = v2 - v0
        face_normal = edge1.cross(edge2).normalized()
        
        vertex_normals[i0] = vertex_normals[i0] + face_normal
        vertex_normals[i1] = vertex_normals[i1] + face_normal
        vertex_normals[i2] = vertex_normals[i2] + face_normal

    for i in range(len(vertex_normals)):
        if vertex_normals[i].length_squared() > 0:
            vertex_normals[i] = vertex_normals[i].normalized()

    diffuse_color = Vector3(obj_data.material.color.r, 
                            obj_data.material.color.g, 
                            obj_data.material.color.b)

    transform = Mat4.identity()
    #transform = Mat4.translation(obj_data.relative_pos) * transform
    for t in obj_data.transforms:
        ttype = t.t_type
        val = t.data
        if ttype == "translation":
            transform = Mat4.translation(val) * transform
        elif ttype == "scaling":
            transform = Mat4.scaling(val.x, val.y, val.z) * transform
        elif ttype == "rotation":
            transform = Mat4.rotation_z(math.radians(val.z)) * transform
            transform = Mat4.rotation_y(math.radians(-val.y)) * transform
            transform = Mat4.rotation_x(math.radians(val.x)) * transform
    #transform = Mat4.translation(obj_data.relative_pos) * transform

    world_vertices = [transform.transform_point(v) for v in local_vertices]
    world_normals = [transform.transform_normal(n) for n in vertex_normals]

    return Mesh(world_vertices, triangles, world_normals, diffuse_color)