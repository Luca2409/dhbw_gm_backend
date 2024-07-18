import math
import mediapipe as mp
import cv2

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def process_image(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    landmark_data = {}
    if results.pose_landmarks:
        for id, landmark in enumerate(results.pose_landmarks.landmark):
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            landmark_data[id] = (x, y)
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        # Speichern des Bildes mit den Landmarken als Bilddatei
        output_image_path = 'output_image_with_landmarks.jpg'
        cv2.imwrite(output_image_path, image)

    return landmark_data


def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_body_measurements(landmark_data, known_height_mm, nose_to_head_top_mm=120):
    measurements = []
    if (mp_pose.PoseLandmark.LEFT_ANKLE.value in landmark_data and
            mp_pose.PoseLandmark.RIGHT_ANKLE.value in landmark_data and
            mp_pose.PoseLandmark.NOSE.value in landmark_data and
            mp_pose.PoseLandmark.LEFT_HIP.value in landmark_data and
            mp_pose.PoseLandmark.RIGHT_HIP.value in landmark_data and
            mp_pose.PoseLandmark.LEFT_SHOULDER.value in landmark_data and
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value in landmark_data):

        left_ankle = landmark_data[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmark_data[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        nose = landmark_data[mp_pose.PoseLandmark.NOSE.value]
        left_shoulder = landmark_data[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmark_data[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmark_data[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmark_data[mp_pose.PoseLandmark.RIGHT_HIP.value]

        # Berechnung der mittleren Position von den Schultern, Hüften und Knöcheln
        mid_shoulder = ((left_shoulder[0] + right_shoulder[0]) // 2, (left_shoulder[1] + right_shoulder[1]) // 2)
        mid_hip = ((left_hip[0] + right_hip[0]) // 2, (left_hip[1] + right_hip[1]) // 2)
        mid_ankle = ((left_ankle[0] + right_ankle[0]) // 2, (left_ankle[1] + right_ankle[1]) // 2)

        # Höhe in Pixel von der Oberseite des Kopfes zu den Knöcheln
        height_in_pixels = mid_ankle[1] - (nose[1] - nose_to_head_top_mm)

        if height_in_pixels <= 0:
            raise ValueError("The calculated height in pixels is invalid.")

        # Maßstab berechnen (mm pro Pixel)
        scale = known_height_mm / height_in_pixels

        try:
            neck_line = (landmark_data[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                         landmark_data[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
            left_shoulder_line = (landmark_data[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                  landmark_data[mp_pose.PoseLandmark.LEFT_ELBOW.value])
            left_elbow_line = (landmark_data[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                               landmark_data[mp_pose.PoseLandmark.LEFT_WRIST.value])
            right_shoulder_line = (landmark_data[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                   landmark_data[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
            right_elbow_line = (landmark_data[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                landmark_data[mp_pose.PoseLandmark.RIGHT_WRIST.value])
            waist_line = (landmark_data[mp_pose.PoseLandmark.LEFT_HIP.value],
                          landmark_data[mp_pose.PoseLandmark.RIGHT_HIP.value])
            hemline = (landmark_data[mp_pose.PoseLandmark.LEFT_ANKLE.value],
                       landmark_data[mp_pose.PoseLandmark.RIGHT_ANKLE.value])

            measurement = {
                "neck_line_mm": calculate_distance(*neck_line) * scale,
                "left_shoulder_line_mm": calculate_distance(*left_shoulder_line) * scale,
                "left_elbow_line_mm": calculate_distance(*left_elbow_line) * scale,
                "right_shoulder_line_mm": calculate_distance(*right_shoulder_line) * scale,
                "right_elbow_line_mm": calculate_distance(*right_elbow_line) * scale,
                "waist_line_mm": calculate_distance(*waist_line) * scale,
                "hemline_mm": calculate_distance(*hemline) * scale,
                "height_pixels": height_in_pixels  # Die gesamte Körpergröße in Pixel
            }
            measurements.append(measurement)
        except KeyError:
            pass

    return measurements
