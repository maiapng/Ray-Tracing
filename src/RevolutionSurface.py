import math
from src.Vector3 import Vector3
from src.Mesh import Mesh
from src.Mat4 import Mat4


def bezier_point(control_points_2d, t):
    points = list(control_points_2d)
    n = len(points)
    for step in range(1, n):
        for i in range(n - step):
            r = points[i][0] * (1 - t) + points[i + 1][0] * t
            h = points[i][1] * (1 - t) + points[i + 1][1] * t
            points[i] = (r, h)
    return points[0]


def generate_revolution_mesh(control_points_2d, curve_steps, radial_steps, material_color, transforms):
    curve_points = []
    for i in range(curve_steps + 1):
        t = i / curve_steps
        radius, height = bezier_point(control_points_2d, t)
        curve_points.append((radius, height))

    vertices = []
    for radius, height in curve_points:
        for ri in range(radial_steps):
            angle = 2 * math.pi * ri / radial_steps
            x = radius * math.cos(angle)
            y = height
            z = radius * math.sin(angle)
            vertices.append(Vector3(x, y, z))

    triangles = []
    for ci in range(curve_steps):
        for ri in range(radial_steps):
            ri_next = (ri + 1) % radial_steps
            top_left     = ci * radial_steps + ri
            top_right    = ci * radial_steps + ri_next
            bottom_left  = (ci + 1) * radial_steps + ri
            bottom_right = (ci + 1) * radial_steps + ri_next
            triangles.append((top_left,  bottom_left,  bottom_right))
            triangles.append((top_left,  bottom_right, top_right))

    vertex_normals = [Vector3(0, 0, 0) for _ in vertices]
    for (i0, i1, i2) in triangles:
        edge1 = vertices[i1] - vertices[i0]
        edge2 = vertices[i2] - vertices[i0]
        face_normal = edge1.cross(edge2).normalized()
        vertex_normals[i0] = vertex_normals[i0] + face_normal
        vertex_normals[i1] = vertex_normals[i1] + face_normal
        vertex_normals[i2] = vertex_normals[i2] + face_normal

    for i in range(len(vertex_normals)):
        if vertex_normals[i].length_squared() > 0:
            vertex_normals[i] = vertex_normals[i].normalized()

    transform = Mat4.identity()
    for t in transforms:
        ttype = t.t_type
        val   = t.data
        if ttype == "translation":
            transform = Mat4.translation(val) * transform
        elif ttype == "scaling":
            transform = Mat4.scaling(val.x, val.y, val.z) * transform
        elif ttype == "rotation":
            transform = Mat4.rotation_z(math.radians(val.z)) * transform
            transform = Mat4.rotation_y(math.radians(-val.y)) * transform
            transform = Mat4.rotation_x(math.radians(val.x)) * transform

    world_vertices = [transform.transform_point(v) for v in vertices]
    world_normals  = [transform.transform_normal(n) for n in vertex_normals]

    return Mesh(world_vertices, triangles, world_normals, material_color)
