import pygame

# Define the Cython types
ctypedef Py_ssize_t ssize_t

# Define the load_image function with type annotations and cdef variables
cdef pygame.Surface load_image(str path, tuple size=None) except +:
    cdef float width_multiplier, height_multiplier
    cdef pygame.Surface image
    width_multiplier, height_multiplier = render.get_size_multiplier()
    image = pygame.image.load(path.encode('utf-8'))
    if size:
        return pygame.transform.smoothscale(image, (int(size[0] * width_multiplier), int(size[1] * height_multiplier)))
    return pygame.transform.smoothscale(image, (int(image.get_width() * width_multiplier), int(image.get_height() * height_multiplier)))

# Define the load_images function with type annotations and a cdef list
cpdef list load_images(list[str] paths, tuple size=None) except +:
    cdef list images = []
    cdef str path
    for path in paths:
        images.append(load_image(path, size))
    return images