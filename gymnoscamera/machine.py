import datetime

import cv2
import gymnos_firestore.machines as machines
from gymnos_firestore import usage
from matchbox.queries.error import DocumentDoesNotExists

TOP_X = "TopX"
LEFT_Y = "LeftY"
BOTTOM_X = "BottomX"
RIGHT_Y = "RightY"


class Machine:
    """
    This class keeps track of machine coordinates and machine usage
    """
    def __init__(self, station: machines.Machines, camera_width, camera_height):
        (top_x, left_y, bottom_x, right_y) = self.convert_station_ratios(station, camera_width, camera_height)
        self.model = station

        # Coordinates
        self.top_x = top_x
        self.left_y = left_y
        self.bottom_x = bottom_x
        self.right_y = right_y

        self.iou_threshold = 0.01
        self.time_threshold = 2  # how many seconds until machine is sure you are in or out

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.border_colour = self.get_machine_colour()

        self.time_used = 0
        self.inside = False
        self.using = False
        self.first_detected = 0
        self.time_elapsed = 0

    def get_machine_colour(self):
        if self.model.name == "squat_rack":
            return 0, 0, 255
        else:
            return 255, 0, 0

    def draw_machine(self, image):
        """
        Draws this machine on the image provided

        :param image:
        :return:
        """
        cv2.putText(image,
                    self.model.name,
                    (self.top_x,
                     self.left_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    self.border_colour,
                    2,
                    cv2.LINE_AA)
        if self.using:
            cv2.rectangle(image,
                          (self.top_x, self.left_y),
                          (self.bottom_x, self.right_y),
                          (0, 255, 0),
                          3)
        elif self.inside:
            cv2.rectangle(image,
                          (self.top_x, self.left_y),
                          (self.bottom_x, self.right_y),
                          self.border_colour,
                          3)
        else:
            cv2.rectangle(image,
                          (self.top_x, self.left_y),
                          (self.bottom_x, self.right_y),
                          self.border_colour,
                          1)

    def convert_station_ratios(self, station: machines.Machines, camera_width: int, camera_height: int):
        """
        This function converts station ratios to real pixel values
        :param station:
        :param camera_width:
        :param camera_height:

        :return:
        """
        top_x = int(station.location[TOP_X] * camera_width)
        left_y = int(station.location[LEFT_Y] * camera_height)
        bottom_x = int(station.location[BOTTOM_X] * camera_width)
        right_y = int(station.location[RIGHT_Y] * camera_height)

        return top_x, left_y, bottom_x, right_y

    def increment_machine_time(self, people, image_cap_time):
        """
        This function checks if a person is using a machine. If
        there is somebody there increment the machine usage time.

        :param people: Co-ordinates of a single person
        :param image_cap_time: The exact time the image was captured on
        """
        highest_iou_value = 0
        # Find out if there is at least one person using the machine
        for person in people:
            (h_top_x, h_left_y, h_bottom_x, h_right_y) = person

            iou_value = self.calculate_iou((self.top_x, self.left_y, self.bottom_x, self.right_y),
                                           (h_top_x, h_left_y, h_bottom_x, h_right_y))

            if iou_value > highest_iou_value:
                highest_iou_value = iou_value

        # if there is somebody in the machine
        if highest_iou_value > self.iou_threshold:
            if self.inside is False:
                self.inside = True
                self.first_detected = image_cap_time
            elif self.inside and not self.using:
                diff = image_cap_time - self.first_detected
                # If they have been using this machine for a set period
                # of time, we can be sure the machine is in use
                if diff > self.time_threshold:
                    self.using = True
                    self.time_elapsed = self.first_detected
        else:
            # Turn off all flags if they are set
            if self.inside:
                self.inside = False

                # if machine was being used log that time
                if self.using:
                    self.using = False
                    self.time_used += image_cap_time - self.first_detected
                    print("Used for: " + str(image_cap_time - self.first_detected))

                    # Send to database
                    start_time, end_time = self.first_detected, image_cap_time
                    self.insert_machine_time(start_time, end_time)

    def insert_machine_time(self, start: int, end: int):
        """
        Inserts a row of machine usage

        :param start: Start of machine usage in Unix time
        :param end: End of machine usage in Unix time
        """
        today = datetime.date.today().strftime("%Y/%m/%d")
        machine_time = '{}#{}'.format(start, end)
        time_used = end - start

        try:
            usage_today = usage.Usage.objects.get(MachineID=self.model.id, Date=today, Name=self.model.name)
        except DocumentDoesNotExists:
            usage_today = usage.Usage()
            usage_today.date = today
            usage_today.machine_id = self.model.id
            usage_today.name = self.model.name
            usage_today.times = []
            usage_today.total_time = 0

        usage_today.times.append(machine_time)
        usage_today.total_time += time_used

        usage_today.save()

    def calculate_iou(self, box_a, box_b):
        """
        Computes the intersection over union value between two boxes

        :param box_a:
        :param box_b:
        :return:
        """
        # determine the (x, y)-coordinates of the intersection rectangle
        x_a = max(box_a[0], box_b[0])
        y_a = max(box_a[1], box_b[1])
        x_b = min(box_a[2], box_b[2])
        y_b = min(box_a[3], box_b[3])

        # compute the area of intersection rectangle
        inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)

        # compute the area of both the prediction and ground-truth
        # rectangles
        box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
        box_b_area = (box_b[2] - box_b[0] + 1) * (box_b[3] - box_b[1] + 1)

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the intersection area
        iou = inter_area / float(box_a_area + box_b_area - inter_area)

        # return the intersection over union value
        # print(iou)
        return iou
