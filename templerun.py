import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
prev_y = None
last_action_time = 0
action_delay = 1  # seconds

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        x, y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])

        if index_tip.x < 0.3 and time.time() - last_action_time > action_delay:
            pyautogui.press('left')
            last_action_time = time.time()
            print("Move Left")
        elif index_tip.x > 0.7 and time.time() - last_action_time > action_delay:
            pyautogui.press('right')
            last_action_time = time.time()
            print("Move Right")

        if prev_y is not None:
            if prev_y - y > 30 and time.time() - last_action_time > action_delay:
                pyautogui.press('up')
                last_action_time = time.time()
                print("Jump")
            elif y - prev_y > 30 and time.time() - last_action_time > action_delay:
                pyautogui.press('down')
                last_action_time = time.time()
                print("Slide")

        prev_y = y

    cv2.imshow("Temple Run Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
