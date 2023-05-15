cimport cython
from libc.math cimport atan2, cos, sin, hypot

def calculate_hand_position(double BODY_RADIUS, double HAND_RADIUS, double angle_offset, double center_pos_x, double center_pos_y, double mouse_pos_x, double mouse_pos_y):
    cdef double distance_x = mouse_pos_x - center_pos_x
    cdef double distance_y = mouse_pos_y - center_pos_y
    cdef double distance_to_mouse = hypot(distance_x, distance_y)
    cdef double normalized_distance_x = distance_x / distance_to_mouse
    cdef double normalized_distance_y = distance_y / distance_to_mouse
    cdef double angle = atan2(normalized_distance_y, normalized_distance_x) + angle_offset
    cdef double cos_angle = cos(angle)
    cdef double sin_angle = sin(angle)
    cdef double hand_pos_x = center_pos_x + BODY_RADIUS * cos_angle - HAND_RADIUS / 2
    cdef double hand_pos_y = center_pos_y + BODY_RADIUS * sin_angle - HAND_RADIUS / 2
    return (hand_pos_x, hand_pos_y)