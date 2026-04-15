import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# Initialize hand detection and drawing modules
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Define hand landmarks and regions for gesture recognition
hand_landmarks = mp_hands.HandLandmark
index_finger_tip = hand_landmarks.INDEX_FINGER_TIP
middle_finger_tip = hand_landmarks.MIDDLE_FINGER_TIP
thumb_tip = hand_landmarks.THUMB_TIP

# Define screen size for mouse movement mapping
screen_width, screen_height = pyautogui.size()

# Thresholds for gesture detection (adjust as needed)
scroll_threshold = 50  # Distance change for scrolling (pixels)
click_threshold = 30  # Distance change for clicking (pixels)
tab_switch_threshold = 100  # Horizontal movement distance for tab switching (pixels)
square_threshold = 50  # Distance change for square gesture (pixels)
def Handgesture():
    def calculate_distance(landmark1, landmark2, results):
        """Calculates the Euclidean distance between two hand landmarks."""
        try:
            landmark1_x = results.multi_hand_landmarks[0].landmark[landmark1].x * screen_width
            landmark1_y = results.multi_hand_landmarks[0].landmark[landmark1].y * screen_height
            landmark2_x = results.multi_hand_landmarks[0].landmark[landmark2].x * screen_width
            landmark2_y = results.multi_hand_landmarks[0].landmark[landmark2].y * screen_height
            return np.sqrt((landmark1_x - landmark2_x) ** 2 + (landmark1_y - landmark2_y) ** 2)
        except (AttributeError, IndexError):
            # Handle cases where landmarks might not be detected
            print("Error: Hand landmarks not detected.")
            return None

    def detect_scroll_gesture(results, previous_thumb_index_distance):
        """Detects scroll gesture based on thumb and index finger distance."""
        current_thumb_index_distance = calculate_distance(thumb_tip, index_finger_tip, results)
        if current_thumb_index_distance is None:
            return previous_thumb_index_distance  # Maintain state if landmarks not detected

        distance_change = abs(current_thumb_index_distance - previous_thumb_index_distance)

        if distance_change > scroll_threshold:
            if current_thumb_index_distance > previous_thumb_index_distance:
                # Scroll down
                pyautogui.scroll(-100)  # Adjust scrolling amount
            else:
                # Scroll up
                pyautogui.scroll(100)  # Adjust scrolling amount

        return current_thumb_index_distance  # Update for next iteration

    def detect_mouse_movement(results, previous_center_x):
        """Detects mouse movement based on thumb finger position."""
        if results.multi_hand_landmarks:
            center_x = (results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].x +
                        results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x) / 2 * screen_width

            movement = center_x - previous_center_x
            if abs(movement) > 10:
                pyautogui.moveRel(movement, 0, duration=0.1)

        return center_x  # Update for next iteration

    def detect_click_gesture(results, previous_thumb_index_distance):
        """Detects click gesture based on thumb and index finger distance."""
        current_thumb_index_distance = calculate_distance(thumb_tip, index_finger_tip, results)
        if current_thumb_index_distance is None:
            return previous_thumb_index_distance  # Maintain state if landmarks not detected

        distance_change = abs(current_thumb_index_distance - previous_thumb_index_distance)

        if distance_change > click_threshold:
            if current_thumb_index_distance < click_threshold:
                pyautogui.click()

        return current_thumb_index_distance  # Update for next iteration

    def detect_tab_switch_gesture(results, previous_center_x):
        """Detects tab switch gesture based on horizontal hand movement."""
        center_x = (results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.WRIST].x +
                    results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x) / 2 * screen_width

        movement = center_x - previous_center_x
        if movement > tab_switch_threshold:
            pyautogui.hotkey('ctrl', 'tab')  # Adjust hotkey for tab switching
        elif movement < -tab_switch_threshold:
            pyautogui.hotkey('ctrl', 'shift', 'tab')  # Adjust hotkey for tab switching back

        return center_x  # Update for next iteration

    def detect_square_gesture(results, previous_square_distance):
        """Detects square gesture for on-screen interaction."""
        square_distance = calculate_distance(index_finger_tip, thumb_tip, results)
        if square_distance is None:
            return previous_square_distance  # Maintain state if landmarks not detected

        distance_change = abs(square_distance - previous_square_distance)

        if distance_change > square_threshold:
            if square_distance > previous_square_distance:
                # Scroll down
                pyautogui.scroll(-100)  # Adjust scrolling amount
            else:
                # Scroll up
                pyautogui.scroll(100)  # Adjust scrolling amount

        return square_distance  # Update for next iteration

    # Initialize hand detection
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        # Open the camera
        cap = cv2.VideoCapture(0)

        # Initialize previous distances for gesture detection
        previous_thumb_index_distance = 0
        previous_center_x = 0
        previous_square_distance = 0

        while True:
            # Read a frame from the camera
            ret, frame = cap.read()

            # Flip the frame horizontally for a more natural view
            frame = cv2.flip(frame, 1)

            # Convert the frame to RGB for hand detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect hands in the frame
            results = hands.process(frame_rgb)

            # Draw hand landmarks on the frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Detect scroll gesture
                    previous_thumb_index_distance = detect_scroll_gesture(
                        results, previous_thumb_index_distance)

                    # Detect click gesture
                    previous_thumb_index_distance = detect_click_gesture(
                        results, previous_thumb_index_distance)

                    # Detect tab switch gesture
                    previous_center_x = detect_tab_switch_gesture(
                        results, previous_center_x)

                    # Detect square gesture
                    previous_square_distance = detect_square_gesture(
                        results, previous_square_distance)

            # Display the frame
            cv2.imshow('Hand Gesture Recognition', frame)

            # Exit if the user presses the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera and close the window
        cap.release()
        cv2.destroyAllWindows()
# Handgesture()