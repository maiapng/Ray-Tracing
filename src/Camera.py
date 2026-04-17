from src.Vector3 import Vector3

class Camera(object):
    def __init__(self, position:Vector3, look_dir:Vector3, screen_distance:int|float, screen_resolution:tuple[int,int]):
        self.position:Vector3 = position
        self.look_dir:Vector3 = look_dir.normalized()
        self.screen_distance:int|float = screen_distance
        self.screen_resolution:tuple[int,int] = screen_resolution

        self.w:Vector3 = -look_dir
        self.u:Vector3 = self.w.get_any_perpendicular()
        self.v:Vector3 = self.w.cross(self.u).normalized()

    def trace_ray(self, scene, pixel_dir:Vector3):
        pass

    def trace_image(self, scene=None):
        screen_position:Vector3 = self.position + self.look_dir*self.screen_distance 
        for x in range(-self.screen_resolution[0], self.screen_resolution[0]+1):
            for y in range(-self.screen_resolution[1], self.screen_resolution[1]+1):
                pixel_position:Vector3 = screen_position + x*self.u + y*self.v
                pixel_dir:Vector3 = (pixel_position - self.position).normalized()
                print(f"({x},{y}): {pixel_dir}")
                self.trace_ray(scene, pixel_dir)