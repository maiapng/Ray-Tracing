# Mesh.py
import math
from pathlib import Path
from src.Vector3 import Vector3
from src.Mat4 import Mat4
from utils.MeshReader.ObjReader import ObjReader

class Mesh:
    """Armazena a geometria da malha já transformada para coordenadas de mundo."""
    def __init__(self, vertices, triangles, vertex_normals, diffuse_color):
        self.vertices = vertices
        self.triangles = triangles
        self.vertex_normals = vertex_normals
        self.diffuse_color = diffuse_color

def load_mesh_from_obj(obj_data):
    # 1. Caminho do ficheiro .obj
    obj_path_str = obj_data.get_property("path")
    if not obj_path_str:
        return None
    obj_path = Path(obj_path_str)

    # 2. Carrega a malha com o ObjReader
    reader = ObjReader(str(obj_path))
    local_vertices = [Vector3(p.x, p.y, p.z) for p in reader.get_vertices()]
    faces_data = reader.get_faces()

    triangles = []
    for face in faces_data:
        # Assume que as faces são triangulares
        if len(face.vertice_indice) >= 3:
            i0, i1, i2 = face.vertice_indice[0:3]
            triangles.append((i0, i1, i2))

    # 3. Calcula as normais das faces para depois fazer a média nos vértices (Gouraud/Phong Shading)
    vertex_normals = [Vector3(0, 0, 0) for _ in range(len(local_vertices))]
    
    for (i0, i1, i2) in triangles:
        v0, v1, v2 = local_vertices[i0], local_vertices[i1], local_vertices[i2]
        edge1 = v1 - v0
        edge2 = v2 - v0
        face_normal = edge1.cross(edge2).normalized()
        
        # Acumula a normal da face em cada vértice que a compõe
        vertex_normals[i0] = vertex_normals[i0] + face_normal
        vertex_normals[i1] = vertex_normals[i1] + face_normal
        vertex_normals[i2] = vertex_normals[i2] + face_normal

    # Normaliza as normais acumuladas nos vértices
    for i in range(len(vertex_normals)):
        if vertex_normals[i].length_squared() > 0:
            vertex_normals[i] = vertex_normals[i].normalized()

    # 4. Processa a cor difusa (kd)
    diffuse_color = Vector3(obj_data.material.color.r, 
                            obj_data.material.color.g, 
                            obj_data.material.color.b)

    # 5. Concatena as transformações (ORDEM CORRIGIDA)
    # Começamos com uma identidade para as transformações locais da lista
    transform = Mat4.identity()
    
    for t in obj_data.transforms:
        ttype = t.t_type
        val = t.data
        if ttype == "translation":
            trans = Mat4.translation(val)
        elif ttype == "scaling":
            trans = Mat4.scaling(val.x, val.y, val.z)
        elif ttype == "rotation":
            # Rotação composta: Z * Y * X
            rot_x = Mat4.rotation_x(val.x)
            rot_y = Mat4.rotation_y(val.y)
            rot_z = Mat4.rotation_z(val.z)
            trans = rot_z * rot_y * rot_x
        else:
            continue
        
        # Multiplica à esquerda para acumular as transformações locais
        transform = trans * transform

    # A translação para a posição final (relativePos) deve ser SEMPRE a última (mais à esquerda)
    transform = Mat4.translation(obj_data.relative_pos) * transform

    # 6. Aplica as transformações nos vértices e nas normais
    world_vertices = [transform.transform_point(v) for v in local_vertices]
    
    # Para as normais, usamos a Inversa Transposta definida no teu Mat4.py
    world_normals = [transform.transform_normal(n) for n in vertex_normals]

    return Mesh(world_vertices, triangles, world_normals, diffuse_color)