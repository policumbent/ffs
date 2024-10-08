import numpy as np
import cv2


colors = {
    'white': (255, 255, 255),
    'red':   (255, 0, 0),
    'green': (0, 255, 0),
    'blue':  (0, 0, 255)
}


class OverlayElement:
    """
    :param type: type of data (speed, distance, etc...)
    :param val: initial value (default: None)
    :param unit: measurement unit
    :param color: color of the writing
    :param transparency: color transparency (255 -> no transparency)
    """
    def __init__(self, type, val=None, unit="", color=colors['white'],
                 transparency=255):
        self.type = type
        self.val = val
        self.unit = unit
        self.color = color + (transparency,)

    def set_value(self, val):
        """
        :param val: new value
        """
        self.val = round(float(val))


class Overlay:
    """
    :param screen_width: default 1024px
    :param screen_height: default 600px
    :param top_left_org: top left origin point for writings
    :param top_right_org: top right origin point for writings
    :param bottom_left_org: bottom left origin point for writings
    :param bottom_right_org: bottom right origin point for writings
    :param font_scale: font dimension
    :param thickness: font thickness
    :param offset: space between lines
    :param rotation: overlay rotation angle in degrees
    :param font: font type, default cv2.FONT_HERSHEY_SIMPLEX
    :param top_left: ordered list of writings in the top left corner
    :param top_middle: ordered list of writings at the top in the middle
    :param top_right: ordered list of writings in the top right corner
    :param bottom_left: ordered list of writings in the bottom left corner
    :param bottom_middle: ordered list of writings at the bottom in the middle
    :param bottom_right: ordered list of writings in the bottom right corner
    """
    def __init__(self, screen_width=1024, screen_height=600,
                 top_left_org = (10, 50), top_right_org = (1014, 50),
                 bottom_left_org = (10, 570), bottom_right_org = (1014, 570),
                 font_scale=1.5, thickness=4, offset=50, rotation=0,
                 font = cv2.FONT_HERSHEY_SIMPLEX,
                 top_left=[], top_middle=[], top_right=[],
                 bottom_left=[], bottom_middle=[], bottom_right=[]):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.top_left_org = top_left_org
        self.top_right_org = top_right_org
        self.bottom_left_org = bottom_left_org
        self.bottom_right_org = bottom_right_org

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
        for i in range(max(len(self.top_left), len(self.top_right))):
            self.top_vert_org.append(top_left_org[1] + i * offset)

        self.bottom_vert_org = []
        for i in range(max(len(self.bottom_left), len(self.bottom_right))):
            self.bottom_vert_org.append(bottom_left_org[1] - i * offset)


    def update_overlay(self):
        """
        updates overlay by creating a new transparent "frame" on which it writes
        data by iterating all the position lists (top_left, top_middle, etc...)
        :return: overlay frame 
        """
        overlay = np.zeros((self.screen_height, self.screen_width, 4), dtype=np.uint8) * 255

        if len(self.top_left) > 0:
            for i, element in enumerate(self.top_left):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                cv2.putText(
                    overlay,
                    msg,
                    (self.top_left_org[0], self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.top_middle) > 0:
            for i, element in enumerate(self.top_middle):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                elem_dim, _ = cv2.getTextSize(
                    msg,
                    self.font,
                    self.font_scale,
                    self.thickness
                )
                
                cv2.putText(
                    overlay,
                    msg,
                    ((self.screen_width - elem_dim[0]) // 2, self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.top_right) > 0:
            for i, element in enumerate(self.top_right):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                elem_dim, _ = cv2.getTextSize(
                    msg,
                    self.font,
                    self.font_scale,
                    self.thickness
                )

                cv2.putText(
                    overlay,
                    msg,
                    (self.top_right_org[0] - elem_dim[0], self.top_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.bottom_left) > 0:
            for i, element in enumerate(self.bottom_left):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                cv2.putText(
                    overlay,
                    msg,
                    (self.bottom_left_org[0], self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.bottom_middle) > 0:
            for i, element in enumerate(self.bottom_middle):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                elem_dim, _ = cv2.getTextSize(
                    msg,
                    self.font,
                    self.font_scale,
                    self.thickness
                )

                cv2.putText(
                    overlay,
                    msg,
                    ((self.screen_width - elem_dim[0]) // 2, self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if len(self.bottom_right) > 0:
            for i, element in enumerate(self.bottom_right):
                if element.val == None:
                    continue

                msg = f"{element.val}{element.unit}"

                elem_dim, _ = cv2.getTextSize(
                    msg,
                    self.font,
                    self.font_scale,
                    self.thickness
                )

                cv2.putText(
                    overlay,
                    msg,
                    (self.bottom_right_org[0] - elem_dim[0], self.bottom_vert_org[i]),
                    self.font,
                    self.font_scale,
                    element.color,
                    self.thickness,
                    bottomLeftOrigin=False
                )

        if self.rotation != 0:
            image_center = tuple(np.array(overlay.shape[1::-1]) / 2)
            rot_mat = cv2.getRotationMatrix2D(image_center, self.rotation, 1.0)
            result = cv2.warpAffine(overlay, rot_mat, overlay.shape[1::-1], flags=cv2.INTER_LINEAR)
            return result

        return overlay
