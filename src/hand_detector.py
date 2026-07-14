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

        # Stable hand tracking coordinates (wrist x, y) and consecutive missing frame counts
        self.track_wrist = {'X': None, 'O': None}
        self.track_missing = {'X': 0, 'O': 0}

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

        # Check if we got any landmark results from MediaPipe
        if not self.results or not self.results.hand_landmarks:
            # Reset filter and gesture states when no hands are present.
            # Increment missing count for both players.
            # Reset tracking coordinates and pinch history only after the hand has been missing for 30 frames.
            for p in ['X', 'O']:
                self.smooth_x[p] = None
                self.smooth_y[p] = None
                self.track_missing[p] += 1
                if self.track_missing[p] >= 30:
                    self.track_wrist[p] = None
                    self.prev_pinched[p] = False
            return telemetry

        h, w, c = img.shape
        
        # 1. Parse all detected hands and extract their wrist coordinates
        detected_list = []
        for landmarks in self.results.hand_landmarks:
            wrist_x = landmarks[0].x * w
            wrist_y = landmarks[0].y * h
            detected_list.append((landmarks, (wrist_x, wrist_y)))
            
        player_hands = {}
        
        # 2. Assign landmarks based on the active game mode
        if game_mode == "AI":
            # Player vs AI: Track only player 'X' (the human). O (AI) never gets a hand.
            if len(detected_list) > 0:
                if self.track_wrist['X'] is not None:
                    # Match the hand closest to X's last tracked wrist position to ignore brief accidental second hands
                    tx, ty = self.track_wrist['X']
                    best_hand = min(detected_list, key=lambda item: np.hypot(item[1][0] - tx, item[1][1] - ty))[0]
                else:
                    # Pick the first hand if no tracking has started yet
                    best_hand = detected_list[0][0]
                player_hands['X'] = best_hand
                self.track_wrist['X'] = (best_hand[0].x * w, best_hand[0].y * h)
                self.track_missing['X'] = 0
            else:
                self.track_missing['X'] += 1
                if self.track_missing['X'] >= 30:
                    self.track_wrist['X'] = None
            
            # AI (O) has no human hand; increment its missing count
            self.track_missing['O'] += 1
            if self.track_missing['O'] >= 30:
                self.track_wrist['O'] = None
                
        else:  # PVP Mode
            # Player 1 is X (default left screen), Player 2 is O (default right screen)
            default_pos = {
                'X': (w / 4.0, h / 2.0),
                'O': (3.0 * w / 4.0, h / 2.0)
            }
            
            # Determine reference positions (last known or fallback defaults)
            ref_pos = {}
            for p in ['X', 'O']:
                if self.track_wrist[p] is not None:
                    ref_pos[p] = self.track_wrist[p]
                else:
                    ref_pos[p] = default_pos[p]
                    
            if len(detected_list) == 1:
                landmarks, pos = detected_list[0]
                dist_x = np.hypot(pos[0] - ref_pos['X'][0], pos[1] - ref_pos['X'][1])
                dist_o = np.hypot(pos[0] - ref_pos['O'][0], pos[1] - ref_pos['O'][1])
                
                # Assign to the player whose reference position is closer to the detected hand
                if dist_x < dist_o:
                    player_hands['X'] = landmarks
                    self.track_wrist['X'] = pos
                    self.track_missing['X'] = 0
                    
                    self.track_missing['O'] += 1
                    if self.track_missing['O'] >= 30:
                        self.track_wrist['O'] = None
                else:
                    player_hands['O'] = landmarks
                    self.track_wrist['O'] = pos
                    self.track_missing['O'] = 0
                    
                    self.track_missing['X'] += 1
                    if self.track_missing['X'] >= 30:
                        self.track_wrist['X'] = None
                        
            elif len(detected_list) >= 2:
                # Two or more hands detected: match to X and O to minimize frame-to-frame movement cost
                h1, pos1 = detected_list[0]
                h2, pos2 = detected_list[1]
                
                # Cost Option A: h1 -> X, h2 -> O
                cost_A = np.hypot(pos1[0] - ref_pos['X'][0], pos1[1] - ref_pos['X'][1]) + \
                         np.hypot(pos2[0] - ref_pos['O'][0], pos2[1] - ref_pos['O'][1])
                         
                # Cost Option B: h2 -> X, h1 -> O
                cost_B = np.hypot(pos2[0] - ref_pos['X'][0], pos2[1] - ref_pos['X'][1]) + \
                         np.hypot(pos1[0] - ref_pos['O'][0], pos1[1] - ref_pos['O'][1])
                         
                if cost_A < cost_B:
                    player_hands['X'] = h1
                    player_hands['O'] = h2
                    self.track_wrist['X'] = pos1
                    self.track_wrist['O'] = pos2
                else:
                    player_hands['X'] = h2
                    player_hands['O'] = h1
                    self.track_wrist['X'] = pos2
                    self.track_wrist['O'] = pos1
                    
                self.track_missing['X'] = 0
                self.track_missing['O'] = 0

        # Reset smoothing filters for any hands not visible in this frame.
        # Only reset the previous pinch state if the hand has been missing for 30 consecutive frames
        # to ensure temporary frame detection drops do not trigger duplicate click events.
        for p in ['X', 'O']:
            if p not in player_hands:
                self.smooth_x[p] = None
                self.smooth_y[p] = None
                if self.track_missing[p] >= 30:
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
