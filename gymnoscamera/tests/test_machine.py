from unittest.mock import Mock

from gymnoscamera import machine


CAMERA_WIDTH = 100
CAMERA_HEIGHT = 100

class TestMachine:

    machine = None
    machines_mock = None

    def set_up(self):
        self.machines_mock = Mock()
        self.machine = machine.Machine(self.machines_mock, camera_width=CAMERA_WIDTH, camera_height=CAMERA_HEIGHT)

    def tear_down(self):
        self.machines_mock = None
        self.machine = None

    def test_get_machine_color(self):
