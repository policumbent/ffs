import numpy as np
import cv2


colors = {
    'white': (255, 255, 255),
    'red':   (255, 0, 0),
    'green': (0, 255, 0),
    'blue':  (0, 0, 255)
}


class OverlayElement:
    def __init__(self, type, val=None, unit=None, color=colors['white'],
                 transparency=255):
        self.type = type
        self.val = val
        self.unit = unit
        self.color = color + (transparency,)

    def set_value(self, val):
        self.val = val


class Overlay:
    def __init__(self, screen_width=1024, screen_height=600,
                 top_left_org = (10, 50), top_left_org = (1014, 50),
                 bottom_left_org = (10, 570), bottom_right_org = (1014, 570),
                 font_scale=1.5, thickness=4, offset=50, rotation=0,
                 font = cv2.FONT_HERSHEY_SIMPLEX,
                 top_left=[], top_middle=[], top_right=[],
                 bottom_left=[], bottom_middle=[], bottom_right=[]):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_scale = font_scale
        self.thickness = thickness
        self.offset = offset
        self.rotation = rotation
        self.font = font

        self.top_left = top_left
        self.top_middle = top_middle
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_middle = bottom_middle
        self.bottom_right = bottom_right

        self.top_vert_org = []
        for i in max(len(self.top_left), len(self.top_right)):
            self.top_vert_org.append(top_left_org[1] + i * offset)

        self.bottom_vert_org = []
        for i in max(len(self.bottom_left), len(self.bottom_right)):
            self.bottom_vert_org.append(bottom_left_org[1] - i * offset)


    def update_overlay(self):
        overlay = np.zeros((self.screen_height, self.screen_width, 4), dtype=np.uint8) * 255
        
        if len(self.top_left) > 0:
            for i, element in enumerate(self.top_left):
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    (self.top_left_org[0], self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.top_middle) > 0:
            for i, element in enumerate(self.top_left):
                elem_dim, _ = cv2.getTextSize(
                    f"{element.val} {element.unit}",
                    self.font,
                    self.font_scale,
                    self.thickness
                )
                
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    ((self.screen_width - elem_dim[0]) // 2, self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.top_right) > 0:
            for i, element in enumerate(self.top_right):
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    (self.top_right_org[0], self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.bottom_left) > 0:
            for i, element in enumerate(self.bottom_left):
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    (self.bottom_left_org[0], self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )
            
        if len(self.bottom_middle) > 0:
            for i, element in enumerate(self.bottom_left):
                elem_dim, _ = cv2.getTextSize(
                    f"{element.val} {element.unit}",
                    self.font,
                    self.font_scale,
                    self.thickness
                )
                
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    ((self.screen_width - elem_dim[0]) // 2, self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )
        
        if len(self.bottom_right) > 0:
            for i, element in enumerate(self.bottom_right):
                cv2.putText(
                    overlay,
                    f"{element.val} {element.unit}",
                    (self.bottom_right_org[0], self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        return overlay
