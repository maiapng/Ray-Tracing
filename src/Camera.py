from src.Vector3 import Vector3

class Camera(object):
    def __init__(self, position:Vector3, screen_position:Vector3, screen_resolution:tuple[int,int]):
        self.position:Vector3 = position
        self.screen_position = screen_position
        self.screen_resolution = screen_resolution
        self.screen_distance = (screen_position - position).length()
        self.look_dir:Vector3 = (screen_position - position).normalized()
        self.up_dir:Vector3 = self.look_dir.get_any_perpendicular()
        self.right_dir:Vector3 = self.look_dir.cross(self.up_dir).normalized()

    def __str__(self):
        # just for testing now
        return f"{self.position}\n{self.screen_distance}\n{self.look_dir}\n{self.up_dir}\n{self.right_dir}"
    