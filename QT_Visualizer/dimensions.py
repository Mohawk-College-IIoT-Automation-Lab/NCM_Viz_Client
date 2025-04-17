class Dimension:

    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if value >= 0:
            self.__x = value
        else:
            raise ValueError("x must be positive")

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if value >= 0:
            self.__y = value
        else:
            raise ValueError("y must be positive")

    @property
    def w(self):
        return self.__w

    @w.setter
    def w(self, value):
        if value >= 0:
            self.__w = value
        else:
            raise ValueError("width must be positive")

    @property
    def h(self):
        return self.__h

    @h.setter
    def h(self, value):
        if value >= 0:
            self.__h = value
        else:
            raise ValueError("height must be positive")