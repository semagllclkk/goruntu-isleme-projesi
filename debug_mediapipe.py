import mediapipe
import os

print(f"Mediapipe file: {mediapipe.__file__}")
print(f"Mediapipe dir: {os.path.dirname(mediapipe.__file__)}")
try:
    print(f"Mediapipe solutions: {mediapipe.solutions}")
except AttributeError as e:
    print(f"Error: {e}")
    print(f"Mediapipe dir contents: {os.listdir(os.path.dirname(mediapipe.__file__))}")
