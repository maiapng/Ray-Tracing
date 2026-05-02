# Mat4.py
import math
from src.Vector3 import Vector3

class Mat4:
    """Matriz 4x4 para transformações afins."""

    def __init__(self, elements=None):
        if elements is None:
            self.m = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        else:
            self.m = [row[:] for row in elements]

    @staticmethod
    def identity():
        return Mat4()

    @staticmethod
    def translation(v: Vector3):
        return Mat4([
            [1.0, 0.0, 0.0, v.x],
            [0.0, 1.0, 0.0, v.y],
            [0.0, 0.0, 1.0, v.z],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def scaling(sx, sy, sz):
        return Mat4([
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def rotation_x(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return Mat4([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -s, 0.0],
            [0.0, s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def rotation_y(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return Mat4([
            [c, 0.0, s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def rotation_z(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return Mat4([
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    def __mul__(self, other):
        """Multiplicação Mat4 * Mat4"""
        result = [[0.0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                result[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
        return Mat4(result)

    def transform_point(self, p: Vector3) -> Vector3:
        x = self.m[0][0]*p.x + self.m[0][1]*p.y + self.m[0][2]*p.z + self.m[0][3]
        y = self.m[1][0]*p.x + self.m[1][1]*p.y + self.m[1][2]*p.z + self.m[1][3]
        z = self.m[2][0]*p.x + self.m[2][1]*p.y + self.m[2][2]*p.z + self.m[2][3]
        w = self.m[3][0]*p.x + self.m[3][1]*p.y + self.m[3][2]*p.z + self.m[3][3]
        if abs(w) > 1e-12 and abs(w - 1.0) > 1e-12:
            return Vector3(x/w, y/w, z/w)
        return Vector3(x, y, z)

    def transform_vector(self, v: Vector3) -> Vector3:
        x = self.m[0][0]*v.x + self.m[0][1]*v.y + self.m[0][2]*v.z
        y = self.m[1][0]*v.x + self.m[1][1]*v.y + self.m[1][2]*v.z
        z = self.m[2][0]*v.x + self.m[2][1]*v.y + self.m[2][2]*v.z
        return Vector3(x, y, z)

    def transform_normal(self, n: Vector3) -> Vector3:
        try:
            inv_t = self.inverse().transpose()
        except ValueError:
            return Vector3(n.x, n.y, n.z).normalized()
        return inv_t.transform_vector(n).normalized()

    def inverse(self):
        a = [row[:] for row in self.m]
        inv = Mat4.identity().m
        for i in range(4):
            pivot = i
            for j in range(i+1, 4):
                if abs(a[j][i]) > abs(a[pivot][i]):
                    pivot = j
            if abs(a[pivot][i]) < 1e-12:
                raise ValueError("Matriz singular")
            a[i], a[pivot] = a[pivot], a[i]
            inv[i], inv[pivot] = inv[pivot], inv[i]
            div = a[i][i]
            for j in range(4):
                a[i][j] /= div
                inv[i][j] /= div
            for j in range(4):
                if j != i:
                    factor = a[j][i]
                    for k in range(4):
                        a[j][k] -= factor * a[i][k]
                        inv[j][k] -= factor * inv[i][k]
        return Mat4(inv)

    def transpose(self):
        t = [[self.m[j][i] for j in range(4)] for i in range(4)]
        return Mat4(t)

    def __repr__(self):
        return '\n'.join([' '.join(f'{x:.3f}' for x in row) for row in self.m])