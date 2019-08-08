from gymnoscamera.machine import Machine


class TestMachine:

    def setUp(self):
        self.machine = Machine()

    def test_calculate_iou_no_intersection(self):
        box1 = [1,1,2,2]
        box2 = [2,2,3,3]

        actual_iou = self.machine.calculate_iou(box1, box2)

        assert 0 == actual_iou
