cimport cython
from libc.math cimport atan2, cos, sin, hypot, fmod

def calculate_hand_position(double[::1] BODY_RADIUS, double[::1] HAND_RADIUS, double angle_offset, double[::1] render_center_pos, double[::1] game_center_pos, double[::1] mouse_pos):
    # Calculate the distance between the mouse position and the render center position
    cdef double distance_x = mouse_pos[0] - render_center_pos[0]
    cdef double distance_y = mouse_pos[1] - render_center_pos[1]
    cdef double distance_to_mouse = hypot(distance_x, distance_y)

    # Normalize the distance to get the direction vector
    cdef double normalized_distance_x
    cdef double normalized_distance_y
    if distance_to_mouse != 0:
        normalized_distance_x = distance_x / distance_to_mouse
        normalized_distance_y = distance_y / distance_to_mouse
    else:
        return None

    # Calculate the angle based on the normalized direction vector and the angle offset
    cdef double angle = atan2(normalized_distance_y, normalized_distance_x) + angle_offset

    # Calculate the cosine and sine of the angle
    cdef double cos_angle = cos(angle)
    cdef double sin_angle = sin(angle)

    # Calculate the position of the hand based on the game center position, body radius, hand radius, and angle
    cdef double hand_pos_x = game_center_pos[0] + BODY_RADIUS[0] * cos_angle - HAND_RADIUS[0]
    cdef double hand_pos_y = game_center_pos[1] + BODY_RADIUS[1] * sin_angle - HAND_RADIUS[1]

    # Return the calculated hand position
    return (hand_pos_x, hand_pos_y)