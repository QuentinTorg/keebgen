from keebgen.better_abc import abstractmethod
import numpy as np
import solid as sl

from .geometry_base import Assembly, PartCollection, LabeledPoint, AnchorCollection
from .connector import Connector

class Finger(Assembly):
    def __init__(self, second_and_third_digit_len, first_digit_len, lean_back_angle):
        super().__init__()
        self._parts = PartCollection()

        finger_tip = LabeledPoint((0, 0, -second_and_third_digit_len), ['finger', 'tip'])
        second_knuckle = LabeledPoint((0, 0, 0), ['finger', 'second_knuckle'])
        first_knuckle = LabeledPoint((0, -first_digit_len, 0), ['finger', 'first_knuckle'])
        first_knuckle.rotate(-lean_back_angle, 0, 0, degrees=True)

        second_to_tip = Connector(AnchorCollection((finger_tip, second_knuckle)), diameter=2)
        first_to_second = Connector(AnchorCollection((second_knuckle, first_knuckle)), diameter=2)

        self._parts.add(first_to_second, "first_digit")
        self._parts.add(second_to_tip, "second_and_third_digits")

        self._anchors = AnchorCollection(self.anchors_by_part("first_digit") + self.anchors_by_part("second_and_third_digits"))

        for part in self._parts:
            part.solid().set_modifier('%')
