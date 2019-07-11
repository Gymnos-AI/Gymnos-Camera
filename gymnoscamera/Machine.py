import time
import cv2


class Machine:
    """
    This class keeps track of machine coordinates and machine usage
    """
    def __init__(self, station, camera_width, camera_height):
        (name, top_x, left_y, bottom_x, right_y) = self.convert_station_ratios(station,
                                                                               camera_width,
                                                                               camera_height)

        self.name = name
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
        self.time_changed = 0
        self.time_elapsed = 0

    def get_machine_colour(self):
        if self.name == "squat_rack":
            return (0, 0, 255)
        else:
            return (255, 0, 0)

    def draw_machine(self, image):
        """
        Draws this machine on the image provided

        :param image:
        :return:
        """
        # display machine areas
        cv2.rectangle(image,
                      (self.top_x, self.left_y),
                      (self.bottom_x, self.right_y),
                      self.border_colour,
                      1)

    def convert_station_ratios(self, station, camera_width, camera_height):
        """
        This function converts station ratios to real pixel values

        :param station:
        :return:
        """
        name, a, b, c, d = station
        w, h = camera_width, camera_height
        top_x, left_y, bottom_x, right_y = int(a * w), int(b * h), int(c * w), int(d * h)

        return name, top_x, left_y, bottom_x, right_y

    def increment_machine_time(self, person, image, time_widget):
        """
        This function checks if a person is using a machine. If
        there is somebody there increment the machine usage time.

        :param person: Co-ordinates of a single person
        :param image: Reference to the frame under prediction
        :param time_widget: Reference to the frame_timer widget
        """
        (h_top_x, h_left_y, h_bottom_x, h_right_y) = person

        iou_value = self.calculate_iou((self.top_x, self.left_y, self.bottom_x, self.right_y),
                                       (h_top_x, h_left_y, h_bottom_x, h_right_y))

        # if there is somebody in the machine
        if iou_value > self.iou_threshold:
            # highlight the box if it is being used
            if self.using:
                cv2.rectangle(image,
                              (self.top_x, self.left_y),
                              (self.bottom_x, self.right_y),
                              self.border_colour,
                              3)
            if self.inside:
                diff = time.time() - self.time_changed
                if diff > self.time_threshold:
                    self.using = True
                    self.time_elapsed = self.time_changed
            else:
                self.inside = True
                self.time_changed = time.time()
        else:
            # turn off machine flag
            if self.inside:
                self.inside = False
                self.time_changed = time.time()
            # update the time used
            else:
                diff = time.time() - self.time_changed
                if diff > self.time_threshold and self.using:
                    self.using = False
                    self.time_used += time.time() - self.time_elapsed - self.time_threshold

        # Update dashboard
        time_widget.update_time(self.name, self.time_used)

    def calculate_iou(self, boxA, boxB):
        """
        Computes the intersection over union value between two boxes

        :param boxA:
        :param boxB:
        :return:
        """
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        # compute the area of intersection rectangle
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the intersection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        # print(iou)
        return iou
