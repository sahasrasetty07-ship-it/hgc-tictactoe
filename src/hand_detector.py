import cv2
import mediapipe as mp
import numpy as np
import config
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandDetector:
    def __init__(self, model_path='hand_landmarker.task', detection_confidence=0.7, tracking_confidence=0.7, num_hands=2):
        """
        Initializes the modern MediaPipe Hand Landmarker Tasks API.
        
        :param model_path: Path to the downloaded hand_landmarker.task model file.
        :param detection_confidence: Min confidence value ([0.0, 1.0]) for hand detection.
        :param tracking_confidence: Min confidence value ([0.0, 1.0]) for hand presence/tracking.
        :param num_hands: Maximum number of hands to detect.
        """
        # Configure Hand Landmarker options
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
            min_tracking_confidence=tracking_confidence
        )
        # Create detector from options
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None

        # Filter states for cursor smoothing
        self.smooth_x = {'X': None, 'O': None}
        self.smooth_y = {'X': None, 'O': None}

        # Gesture tracking state
        self.prev_pinched = {'X': False, 'O': False}

    def process_interaction(self, img, timestamp_ms, game_mode="AI", draw=True):
        """
        Runs hand tracking, overlays the skeleton overlay, smooths the index tip coordinates,
        detects pinch states, and returns diagnostic gesture telemetry for both players X and O.
        
        :param img: OpenCV BGR image frame.
        :param timestamp_ms: Simple monotonically increasing frame timestamp in milliseconds.
        :param game_mode: Game mode string ("AI" or "PVP").
        :param draw: Boolean to draw hand skeleton.
        :return: Dict of telemetry per player, or empty dict if no hands detected.
        """
        # Convert BGR frame to RGB for MediaPipe Tasks
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Perform detection for video mode
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        telemetry = {}

        if not self.results or not self.results.hand_landmarks:
            # Reset filter and gesture states when no hands are present
            for p in ['X', 'O']:
                self.smooth_x[p] = None
                self.smooth_y[p] = None
                self.prev_pinched[p] = False
            return telemetry

        h, w, c = img.shape
        detected_hands = []
        for landmarks in self.results.hand_landmarks:
            wrist_x = landmarks[0].x * w
            detected_hands.append((landmarks, wrist_x))
        
        # Sort hands by horizontal coordinate (left to right)
        detected_hands.sort(key=lambda item: item[1])
        
        # Assign landmarks to player designations based on horizontal side and mode
        player_hands = {}
        if game_mode == "AI":
            # In Player vs AI, the human is Player X and controls the game using any single hand in view
            if len(detected_hands) >= 1:
                player_hands['X'] = detected_hands[0][0]
        else: # "PVP"
            if len(detected_hands) == 1:
                landmarks, wrist_x = detected_hands[0]
                if wrist_x < w // 2:
                    player_hands['X'] = landmarks
                else:
                    player_hands['O'] = landmarks
            elif len(detected_hands) >= 2:
                player_hands['X'] = detected_hands[0][0]
                player_hands['O'] = detected_hands[1][0]

        # Reset states for any players whose hands are not in view
        for p in ['X', 'O']:
            if p not in player_hands:
                self.smooth_x[p] = None
                self.smooth_y[p] = None
                self.prev_pinched[p] = False

        # Process each active hand
        for p, landmarks in player_hands.items():
            # 1. Draw hand skeleton overlay
            if draw:
                joint_color = config.COLOR_X if p == 'X' else config.COLOR_O
                
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
                    pt1 = landmarks[start_idx]
                    pt2 = landmarks[end_idx]
                    x1, y1 = int(pt1.x * w), int(pt1.y * h)
                    x2, y2 = int(pt2.x * w), int(pt2.y * h)
                    cv2.line(img, (x1, y1), (x2, y2), (200, 200, 200), 2, cv2.LINE_AA)
                
                # Draw joint dots using the player color
                for lm in landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 6, joint_color, cv2.FILLED, cv2.LINE_AA)
                    cv2.circle(img, (cx, cy), 6, (20, 100, 20), 1, cv2.LINE_AA)

            # 2. Extract Thumb Tip (ID 4) and Index Tip (ID 8)
            thumb_lm = landmarks[4]
            index_lm = landmarks[8]
            
            tx, ty = int(thumb_lm.x * w), int(thumb_lm.y * h)
            ix, iy = int(index_lm.x * w), int(index_lm.y * h)

            # 3. Apply Exponential Moving Average (EMA) smoothing to index fingertip coordinates
            if self.smooth_x[p] is None or self.smooth_y[p] is None:
                self.smooth_x[p] = float(ix)
                self.smooth_y[p] = float(iy)
            else:
                self.smooth_x[p] = config.SMOOTHING_FACTOR * ix + (1 - config.SMOOTHING_FACTOR) * self.smooth_x[p]
                self.smooth_y[p] = config.SMOOTHING_FACTOR * iy + (1 - config.SMOOTHING_FACTOR) * self.smooth_y[p]

            # 4. Calculate Euclidean distance in pixels between the tips
            pinch_dist = np.hypot(ix - tx, iy - ty)

            # 5. Single-click pinch state machine (requires releasing pinch to re-trigger)
            is_pinched = pinch_dist < config.PINCH_THRESHOLD
            click_triggered = False
            
            if is_pinched and not self.prev_pinched[p]:
                click_triggered = True
                
            self.prev_pinched[p] = is_pinched

            telemetry[p] = {
                "cx": int(self.smooth_x[p]),
                "cy": int(self.smooth_y[p]),
                "pinch_dist": pinch_dist,
                "is_pinched": is_pinched,
                "click_triggered": click_triggered
            }

        return telemetry

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
