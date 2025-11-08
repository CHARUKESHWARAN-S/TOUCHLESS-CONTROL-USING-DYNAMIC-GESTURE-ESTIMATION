import cv2
import mediapipe as mp
import pyautogui
import time
import math
import win32api
import win32con
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# ---------- Setup ----------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Screen size for cursor movement
screen_w, screen_h = pyautogui.size()

# Windows virtual key codes
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

# ---------- Volume Setup ----------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_min, vol_max = volume.GetVolumeRange()[:2]

# ---------- Helper Functions ----------
def press_media_key(vk_code):
    """Simulate pressing a system media key."""
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

def distance(p1, p2):
    """Calculate Euclidean distance between two landmarks."""
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def fingers_up(hand_landmarks):
    """Count how many fingers are up."""
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_mcps = [
        mp_hands.HandLandmark.INDEX_FINGER_MCP,
        mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
        mp_hands.HandLandmark.RING_FINGER_MCP,
        mp_hands.HandLandmark.PINKY_MCP
    ]

    fingers = []
    for tip, mcp in zip(finger_tips, finger_mcps):
        fingers.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y)
    return sum(fingers)

def thumb_direction(landmarks):
    """Detect thumb direction (Up / Down / Neutral)."""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]
    if thumb_tip.y < thumb_mcp.y and thumb_tip.y < index_mcp.y:
        return "UP"
    elif thumb_tip.y > thumb_mcp.y and thumb_tip.y > pinky_mcp.y:
        return "DOWN"
    return "NEUTRAL"

def perform_action(finger_count):
    """Perform media control actions."""
    if finger_count == 2:
        press_media_key(VK_MEDIA_PLAY_PAUSE)
        return "▶️ Play"
    elif finger_count == 3:
        press_media_key(VK_MEDIA_PLAY_PAUSE)
        return "⏸ Pause"
    elif finger_count == 4:
        press_media_key(VK_MEDIA_NEXT_TRACK)
        return "⏭ Next Track"
    elif finger_count == 5:
        press_media_key(VK_MEDIA_PREV_TRACK)
        return "⏮ Previous Track"
    return ""

# ---------- Main ----------
cap = cv2.VideoCapture(0)
prev_time = 0
action_text = ""
action_show_time = 0

print("🎶 Gesture Control Started")
print("✌️ 2 Fingers → Play")
print("🤟 3 Fingers → Pause")
print("✋ 4 Fingers → Next")
print("🖐 5 Fingers → Previous")
print("☝️ 1 Finger → Cursor Move")
print("👍 Thumb Up → Volume Up")
print("👎 Thumb Down → Volume Down")
print("ESC → Exit")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    h, w, _ = frame.shape
    gesture_text = ""

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            count = fingers_up(hand_landmarks)
            gesture_text = f"Fingers: {count}"

            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Cursor move when only index finger up
            if count == 1:
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                pyautogui.moveTo(screen_w - (x * screen_w / w), y * screen_h / h, duration=0.05)
                action_text = "🖱 Cursor Move"
                action_show_time = time.time()

            # Volume Control (Thumb gestures)
            direction = thumb_direction(hand_landmarks.landmark)
            if time.time() - prev_time > 0.6:
                if direction == "UP":
                    current_vol = volume.GetMasterVolumeLevel()
                    new_vol = min(current_vol + 1.0, vol_max)
                    volume.SetMasterVolumeLevel(new_vol, None)
                    action_text = "🔊 Volume Up"
                    action_show_time = time.time()
                    prev_time = time.time()
                elif direction == "DOWN":
                    current_vol = volume.GetMasterVolumeLevel()
                    new_vol = max(current_vol - 1.0, vol_min)
                    volume.SetMasterVolumeLevel(new_vol, None)
                    action_text = "🔉 Volume Down"
                    action_show_time = time.time()
                    prev_time = time.time()

            # Spotify controls (2–5 fingers)
            if count in [2, 3, 4, 5] and (time.time() - prev_time > 1):
                action_text = perform_action(count)
                if action_text:
                    action_show_time = time.time()
                prev_time = time.time()

    # Display gesture info
    cv2.putText(frame, gesture_text, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    if action_text and time.time() - action_show_time < 1.5:
        cv2.putText(frame, action_text, (int(w/2)-170, int(h/2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,255), 4, cv2.LINE_AA)

    cv2.imshow("Gesture-Based Spotify & Volume Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
