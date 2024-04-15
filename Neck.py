import cv2
import mediapipe as mp
import time
import math
# Code for algo for neckease

# Initialize MediaPipe Pose class.
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Capture video from the webcam.
cap = cv2.VideoCapture(0)

# Initialize the start time.
start_time = None

def calculate_angle(a, b, c):
    """Calculate the angle between vector AB and BC."""
    ab = [b.x - a.x, b.y - a.y]  # Vector AB
    cb = [b.x - c.x, b.y - c.y]  # Vector BC
    dot_product = ab[0] * cb[0] + ab[1] * cb[1]  # Dot product
    magnitude_ab = math.sqrt(ab[0] ** 2 + ab[1] ** 2)  # Magnitude of AB
    magnitude_cb = math.sqrt(cb[0] ** 2 + cb[1] ** 2)  # Magnitude of CB
    angle = math.acos(dot_product / (magnitude_ab * magnitude_cb))  # Angle in radians
    angle_deg = math.degrees(angle)  # Convert to degrees
    return angle_deg

last_check_time = time.time()  # Time when we last checked the angle condition
alert_display_time = 0  # Time to start displaying the alert
in_range_start_time = None  # Time when the angle first was in the desired range

# Setup MediaPipe instance.
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        # Check if tracking has started and start the timer.
        if start_time is None:
            start_time = time.time()

        # Calculate the elapsed time.
        elapsed_time = time.time() - start_time
        current_time = time.time()

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and detect the pose.
        results = pose.process(image)

        # Convert the RGB image back to BGR.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # Get required landmarks.
            landmarks = results.pose_landmarks.landmark
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            neck = type('', (), {})()  # Create an empty object for the neck
            neck.x = (left_shoulder.x + right_shoulder.x) / 2
            neck.y = (left_shoulder.y + right_shoulder.y) / 2

            # Calculate the angle
            angle = calculate_angle(left_shoulder, neck, nose)

            # Start tracking the duration the angle is within the desired range
            if 85 <= angle <= 105:
                if in_range_start_time is None:
                    in_range_start_time = current_time
            else:
                in_range_start_time = None  # Reset if out of range

            # Check if the angle has been within the range for 30 seconds
            if in_range_start_time and (current_time - in_range_start_time >= 30):
                in_range_start_time = None  # Reset timer
                alert_display_time = current_time  # Start displaying alert

        # Display alert message if time condition is met
        if alert_display_time and (current_time - alert_display_time < 3):
            cv2.putText(image, "Exercise Time", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the angle
        cv2.putText(image, f"Angle: {int(angle)} deg", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display the timer on the image.
        cv2.putText(image, f"Timer: {int(elapsed_time)}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the image.
        cv2.imshow('Mediapipe Feed', image)

        # Press 'q' to quit the loop.
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Release the capture and destroy any OpenCV windows.
cap.release()
cv2.destroyAllWindows()