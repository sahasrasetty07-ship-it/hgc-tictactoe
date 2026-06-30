import cv2
import mediapipe as mp
import numpy as np
import config
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandDetector:
    def __init__(self, model_path='hand_landmarker.task', detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initializes the modern MediaPipe Hand Landmarker Tasks API.
        
        :param model_path: Path to the downloaded hand_landmarker.task model file.
        :param detection_confidence: Min confidence value ([0.0, 1.0]) for hand detection.
        :param tracking_confidence: Min confidence value ([0.0, 1.0]) for hand presence/tracking.
        """
        # Configure Hand Landmarker options
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
            min_tracking_confidence=tracking_confidence
        )
        # Create detector from options
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None

        # Filter states for cursor smoothing
        self.smooth_x = None
        self.smooth_y = None

        # Gesture tracking state
        self.prev_pinched = False

    def process_interaction(self, img, timestamp_ms, draw=True):
        """
        Runs hand tracking, overlays the skeleton overlay, smooths the index tip coordinates,
        detects pinch states, and returns diagnostic gesture telemetry.
        
        :param img: OpenCV BGR image frame.
        :param timestamp_ms: Timestamp in milliseconds of the video frame.
        :param draw: Boolean to draw hand skeleton.
        :return: Dict containing telemetry if hand detected, None otherwise.
        """
        # Convert BGR frame to RGB for MediaPipe Tasks
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Perform detection for video mode
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        if not self.results or not self.results.hand_landmarks:
            # Reset filter and gesture states when no hand is present
            self.smooth_x = None
            self.smooth_y = None
            self.prev_pinched = False
            return None

        h, w, c = img.shape
        hand_landmarks = self.results.hand_landmarks[0]
        
        # 1. Draw hand skeleton overlay
        if draw:
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
                (0, 5), (5, 6), (6, 7), (7, 8),      # Index
                (5, 9), (9, 10), (10, 11), (11, 12),  # Middle
                (9, 13), (13, 14), (14, 15), (15, 16), # Ring
                (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
                (0, 17)                              # Wrist bottom connection
            ]

            # Draw connection lines (soft grey lines)
            for start_idx, end_idx in connections:
                pt1 = hand_landmarks[start_idx]
                pt2 = hand_landmarks[end_idx]
                x1, y1 = int(pt1.x * w), int(pt1.y * h)
                x2, y2 = int(pt2.x * w), int(pt2.y * h)
                cv2.line(img, (x1, y1), (x2, y2), (200, 200, 200), 2, cv2.LINE_AA)
            
            # Draw joint dots (vibrant green with borders)
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 6, (0, 255, 0), cv2.FILLED, cv2.LINE_AA)
                cv2.circle(img, (cx, cy), 6, (20, 100, 20), 1, cv2.LINE_AA)

        # 2. Extract Thumb Tip (ID 4) and Index Tip (ID 8)
        thumb_lm = hand_landmarks[4]
        index_lm = hand_landmarks[8]
        
        tx, ty = int(thumb_lm.x * w), int(thumb_lm.y * h)
        ix, iy = int(index_lm.x * w), int(index_lm.y * h)

        # 3. Apply Exponential Moving Average (EMA) smoothing to index fingertip coordinates
        if self.smooth_x is None or self.smooth_y is None:
            self.smooth_x = float(ix)
            self.smooth_y = float(iy)
        else:
            self.smooth_x = config.SMOOTHING_FACTOR * ix + (1 - config.SMOOTHING_FACTOR) * self.smooth_x
            self.smooth_y = config.SMOOTHING_FACTOR * iy + (1 - config.SMOOTHING_FACTOR) * self.smooth_y

        # 4. Calculate Euclidean distance in pixels between the tips
        pinch_dist = np.hypot(ix - tx, iy - ty)

        # 5. Single-click pinch state machine (requires releasing pinch to re-trigger)
        is_pinched = pinch_dist < config.PINCH_THRESHOLD
        click_triggered = False
        
        if is_pinched and not self.prev_pinched:
            click_triggered = True
            
        self.prev_pinched = is_pinched

        return {
            "cx": int(self.smooth_x),
            "cy": int(self.smooth_y),
            "pinch_dist": pinch_dist,
            "is_pinched": is_pinched,
            "click_triggered": click_triggered
        }

    def find_hands(self, img, timestamp_ms, draw=True):
        """Legacy compatibility interface; delegates to process_interaction."""
        self.process_interaction(img, timestamp_ms, draw=draw)
        return img

    def find_positions(self, img):
        """Legacy compatibility interface for extracting coordinates."""
        landmark_list = []
        if self.results and self.results.hand_landmarks:
            h, w, c = img.shape
            for lm_id, lm in enumerate(self.results.hand_landmarks[0]):
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([lm_id, cx, cy])
        return landmark_list

    def close(self):
        """Closes the underlying hand landmarker object to release system resources."""
        if hasattr(self, 'detector') and self.detector is not None:
            self.detector.close()
            self.detector = None
