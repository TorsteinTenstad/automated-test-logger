import random
import time

from automated_test_logger import AutomatedTestLogger, use_automated_test_logger

class VirtualDummyInstrument:
    def __init__(self, logger: AutomatedTestLogger = None):
        self._automated_test_logger = logger

    @use_automated_test_logger
    def set_x(self, x):
        self._x = x

    @use_automated_test_logger
    def set_y(self, y):
        self._y = y

    @use_automated_test_logger
    def get_z(self):
        return (self._x, random.random())
    
    @use_automated_test_logger
    def get_w(self):
        return {'A': self._x, 'B': self._y}


if __name__ == '__main__':
    logger = AutomatedTestLogger()
    inst = VirtualDummyInstrument(logger)

    inst.set_x(10)
    inst.set_y(10)
    for i in range(10):
        time.sleep(2)
        inst.get_z()
        inst.get_w()
    
    time.sleep(2)
    inst.set_x(20)
    for i in range(10):
        time.sleep(2)
        inst.get_z()
        inst.get_w()