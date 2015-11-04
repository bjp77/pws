class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class conversions(object):
    @staticmethod
    def temp_f_to_c(temp_f):
        return 0

    @staticmethod
    def temp_c_to_f(temp_c):
        return 0

    #todo other conversions

class computed(object):
    @staticmethod
    def dewpoint(temp, humidity):
        return 0

    @staticmethod
    def windchill(temp, windspeed, humidity):
        return 0


