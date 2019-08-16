import tensorflow as tf
import cv2
import colorsys
import numpy as np
import os
from gymnoscamera.yolo_network.model import yolo_eval
from keras import backend as K

input_names = ['input_1']
output_names = ['conv2d_59/BiasAdd', 'conv2d_67/BiasAdd', 'conv2d_75/BiasAdd']


class Yolo_v3_rt:

    _defaults = {
        "model_path": None,
        "anchors_path": 'model_data/yolo_anchors.txt',
        "classes_path": 'model_data/coco_classes.txt',
        "score": 0.3,
        "iou": 0.45,
        "model_image_size": (256, 256),
        "gpu_num": 1,
    }

    def __init__(self):
        self.__dict__.update(self._defaults)  # set up default values

        self.tf_sess = self.load_tf_rt_graph()

        self.output_tensor = []
        self.output_tensor.append(self.tf_sess.graph.get_tensor_by_name('conv2d_59/BiasAdd:0'))
        self.output_tensor.append(self.tf_sess.graph.get_tensor_by_name('conv2d_67/BiasAdd:0'))
        self.output_tensor.append(self.tf_sess.graph.get_tensor_by_name('conv2d_75/BiasAdd:0'))

        self.input_tensor = self.tf_sess.graph.get_tensor_by_name('input_1:0')

        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.boxes, self.scores, self.classes = self.generate()

    def get_frozen_graph(self, graph_file):
        """Read Frozen Graph file from disk."""
        with tf.gfile.FastGFile(graph_file, "rb") as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
        return graph_def

    def load_tf_rt_graph(self):
        tf.keras.backend.clear_session()

        trt_graph = self.get_frozen_graph('./trt_graph.pb')

        # Create session and load graph
        tf_config = tf.ConfigProto()
        tf_config.gpu_options.allow_growth = True
        tf_sess = tf.Session(config=tf_config)
        tf.import_graph_def(trt_graph, name='')

        return tf_sess

    def _get_class(self):
        classes_path = os.path.expanduser(os.path.join(os.path.dirname(__file__), self.classes_path))
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]

        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(os.path.join(os.path.dirname(__file__), self.anchors_path))
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]

        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        # Generate colors for drawing bounding boxes.
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        np.random.seed(10101)  # Fixed seed for consistent colors across runs.
        np.random.shuffle(self.colors)  # Shuffle colors to decorrelate adjacent classes.
        np.random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2,))

        boxes, scores, classes = yolo_eval(self.output_tensor, self.anchors,
                                           len(self.class_names), self.input_image_shape,
                                           score_threshold=self.score, iou_threshold=self.iou)

        return boxes, scores, classes

    def detect_image(self, image):
        image_data = np.array(image, dtype='float32')

        (image_height, image_width, channels) = image_data.shape

        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.tf_sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.input_tensor: image_data,
                self.input_image_shape: [image_height, image_width],
            })
        print(out_boxes.shape)
        list_of_coords = []
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]

            if predicted_class == "person":
                box = out_boxes[i]

                top, left, bottom, right = box
                top = max(0, np.floor(top + 0.5).astype('int32'))
                left = max(0, np.floor(left + 0.5).astype('int32'))
                bottom = min(image_height, np.floor(bottom + 0.5).astype('int32'))
                right = min(image_width, np.floor(right + 0.5).astype('int32'))

                list_of_coords.append((left + i, top + i, right - i, bottom - i))

        return list_of_coords
