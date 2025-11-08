# 🖐 Touchless Control using Dynamic Gesture Estimation

An AI-powered system that enables *hands-free computer interaction* through *real-time dynamic hand gesture recognition*.  
Built using *MediaPipe, **OpenCV, and **Python, it detects and interprets gestures to perform actions like **volume adjustment, **cursor control, and **media playback* — all without physical touch.

---

## 🚀 Features
- Real-time hand tracking using *MediaPipe*
- Dynamic gesture recognition for multiple actions
- Smooth and responsive gesture-to-action mapping
- Works with any standard webcam
- Cross-platform support (Windows/Linux)

---

## 🧠 Tech Stack
- *Language:* Python  
- *Libraries:* MediaPipe, OpenCV, NumPy, TensorFlow, PyAutoGUI  
- *Model:* LSTM / CNN-based gesture sequence recognition  
- *Interface:* Command-line / Visual overlay feedback  

---

## ⚙ System Workflow
1. Capture hand movements via webcam  
2. Extract 21 hand landmarks using MediaPipe  
3. Process temporal frames for gesture patterns  
4. Recognize gestures using trained model  
5. Map recognized gestures to system-level actions  

---

## 📂 Project Structure
📦 touchless-control
┣ 📜 requirements.txt # Dependencies
┣ 📜 LICENSE # MIT License
┗ 📜 README.md # Project description



---
## Perform gestures like:

☝️ Index finger only - 🎯 Cursor Control

👍 / 👎 Thumb Up / Down – 🔊 Volume Up / Down

🖖 Three fingers up (index + middle + ring) – ▶️ Play / Pause

✋ Four fingers up (no thumb) – ⏭️ Next Track

✋ Five fingers up - ⏮️ Previous Track

---

## 🧩 Installation
```bash
git clone https://github.com/CHARUKESHWARAN-S/TOUCHLESS-CONTROL-USING-DYNAMIC-GESTURE-ESTIMATION.git
cd touchless-control
pip install -r requirements.txt
python main.py


