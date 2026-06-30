import cv2
import numpy as np
import time
import random
import config
from src.menu import check_button_hover, draw_menu
from src.hand_detector import HandDetector
from src.game_logic import TicTacToe
from src.ui_renderer import (
    draw_board, draw_hud, draw_cursor, draw_debug_panel, 
    draw_scoreboard, draw_winning_line, draw_game_over_overlay, 
    check_end_button_hover
)

class GameManager:
    def __init__(self):
        self.state = config.STATE_MENU
        self.running = True
        self.mouse_x = 0
        self.mouse_y = 0
        self.hovered_btn = None
        
        # Game state engine
        self.game = TicTacToe()
        
        # Difficulty setting: "Easy", "Medium", or "Hard"
        self.difficulty = "Hard"
        
        # Webcam & hand tracking placeholders
        self.cap = None
        self.detector = None
        
        # FPS timing tracking
        self.prev_time = 0
        
        # Win-line growth progress (0.0 to 1.0)
        self.win_line_progress = 0.0
        # Hover tracking for Game Over panel buttons
        self.end_hovered_btn = None
        
        # AI Opponent states
        self.ai_thinking = False
        self.ai_start_time = 0.0
        self.ai_delay = 0.0
        
        # Create window once
        cv2.namedWindow(config.WINDOW_NAME)
        # Register mouse callback
        cv2.setMouseCallback(config.WINDOW_NAME, self._mouse_callback)

    def _mouse_callback(self, event, x, y, flags, param):
        """Internal callback for mouse events from OpenCV."""
        self.mouse_x = x
        self.mouse_y = y

        if self.state == config.STATE_MENU:
            self.hovered_btn = check_button_hover(x, y)
            if event == cv2.EVENT_LBUTTONDOWN:
                if self.hovered_btn == "START":
                    self.transition_to_game()
                elif self.hovered_btn == "DIFFICULTY":
                    self._cycle_difficulty()
                elif self.hovered_btn == "EXIT":
                    print("Exit button clicked.")
                    self.running = False
        
        elif self.state == config.STATE_GAME:
            # Prevent manual moves if AI is thinking
            if self.game.game_over:
                self.end_hovered_btn = check_end_button_hover(x, y)
                if event == cv2.EVENT_LBUTTONDOWN:
                    if self.end_hovered_btn == "PLAY":
                        print("Mouse clicked Play Again.")
                        self.game.reset()
                        self.win_line_progress = 0.0
                        self.end_hovered_btn = None
                    elif self.end_hovered_btn == "MENU_BTN":
                        print("Mouse clicked Main Menu.")
                        self.transition_to_menu()

    def _cycle_difficulty(self):
        """Cycles through difficulties: Easy -> Medium -> Hard."""
        if self.difficulty == "Easy":
            self.difficulty = "Medium"
        elif self.difficulty == "Medium":
            self.difficulty = "Hard"
        else:
            self.difficulty = "Easy"
        print(f"AI Difficulty changed to: {self.difficulty}")

    def transition_to_game(self):
        """Initializes the webcam, hand detector, resets game board, and transitions state to Game."""
        print("Starting game... Opening webcam.")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            self.cap = None
            return
        
        # Set dimensions if camera supports it
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.HEIGHT)
        
        # Reset TicTacToe board state
        self.game.reset()
        self.win_line_progress = 0.0
        self.end_hovered_btn = None
        self.ai_thinking = False
        
        # Instantiate Hand Detector
        print("Initializing MediaPipe Hand Landmarker...")
        self.detector = HandDetector()
        
        # Initialize timing for FPS
        self.prev_time = time.time()
        
        self.state = config.STATE_GAME

    def transition_to_menu(self):
        """Releases the webcam, closes hand detector, and transitions back to Menu."""
        print("Returning to menu... Releasing webcam.")
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.detector is not None:
            self.detector.close()
            self.detector = None
        self.state = config.STATE_MENU

    def run(self):
        """Main application loop."""
        # Menu frame cache (pre-allocated)
        menu_frame = np.zeros((config.HEIGHT, config.WIDTH, 3), dtype=np.uint8)

        while self.running:
            if self.state == config.STATE_MENU:
                # 1. Update and draw menu
                draw_menu(menu_frame, self.hovered_btn, self.difficulty)
                
                # Check for hand inputs in menu state
                if self.detector is not None:
                    # Normally webcam is off in menu, but if detector exists we can query it
                    pass
                
                cv2.imshow(config.WINDOW_NAME, menu_frame)
                
                # 2. Key input: 'q' / 'Q' or Esc exits
                key = cv2.waitKey(33) & 0xFF  # ~30 FPS limit on menu loop
                if key == ord('q') or key == ord('Q') or key == 27:
                    print("Quit key pressed in menu.")
                    self.running = False

            elif self.state == config.STATE_GAME:
                # 1. Capture webcam frame
                if self.cap is None or self.detector is None:
                    self.transition_to_menu()
                    continue
                
                success, frame = self.cap.read()
                if not success:
                    print("Error: Failed to grab webcam frame.")
                    self.transition_to_menu()
                    continue

                # Flip frame for natural mirror effect
                frame = cv2.flip(frame, 1)

                # Get monotonically increasing timestamp in milliseconds
                timestamp_ms = int(time.time() * 1000)

                # 2. Handle AI Thinking State Machine (Automatic turn for O)
                if not self.game.game_over and self.game.current_player == 'O':
                    if not self.ai_thinking:
                        # Initialize AI delay timer
                        self.ai_thinking = True
                        self.ai_start_time = time.time()
                        self.ai_delay = random.uniform(0.6, 0.8) # 600 to 800ms
                    else:
                        # Wait for delay to expire
                        if time.time() - self.ai_start_time >= self.ai_delay:
                            ai_move = self.game.get_ai_move(self.difficulty)
                            if ai_move is not None:
                                r_ai, c_ai = ai_move
                                self.game.make_move(r_ai, c_ai)
                                print(f"AI ({self.difficulty}) placed mark O at Row {r_ai}, Col {c_ai}")
                            self.ai_thinking = False

                # 3. Increment winning line animation progress if win occurred
                if self.game.game_over and self.game.winner in ('X', 'O'):
                    if self.win_line_progress < 1.0:
                        self.win_line_progress = min(1.0, self.win_line_progress + 0.05)

                # 4. Detect hand, get interaction telemetry
                telemetry = self.detector.process_interaction(frame, timestamp_ms, draw=True)

                # Active grid cell selection tracking
                active_cell = None
                
                if telemetry is not None:
                    cx, cy = telemetry["cx"], telemetry["cy"]
                    
                    # Lock input while game is over OR while AI is thinking
                    if not self.game.game_over and not self.ai_thinking:
                        # 4a. Map cursor position to grid cell (row, col)
                        if (config.BOARD_X_START <= cx < config.BOARD_X_START + config.BOARD_SIZE) and \
                           (config.BOARD_Y_START <= cy < config.BOARD_Y_START + config.BOARD_SIZE):
                            col = (cx - config.BOARD_X_START) // config.CELL_SIZE
                            row = (cy - config.BOARD_Y_START) // config.CELL_SIZE
                            
                            row = max(0, min(2, row))
                            col = max(0, min(2, col))
                            active_cell = (row, col)
                        
                        # 4b. Handle grid click triggers
                        if telemetry["click_triggered"] and active_cell is not None:
                            success_move = self.game.make_move(row, col)
                            if success_move:
                                print(f"Placed mark at Row {row}, Col {col}. Next turn: {self.game.current_player}")
                    
                    elif self.game.game_over:
                        # 4c. If game is over, map cursor position to game over buttons
                        self.end_hovered_btn = check_end_button_hover(cx, cy)
                        if telemetry["click_triggered"] and self.end_hovered_btn is not None:
                            if self.end_hovered_btn == "PLAY":
                                print("Pinch triggered Play Again.")
                                self.game.reset()
                                self.win_line_progress = 0.0
                                self.end_hovered_btn = None
                            elif self.end_hovered_btn == "MENU_BTN":
                                print("Pinch triggered Main Menu.")
                                self.transition_to_menu()
                                continue

                    # Render passive/active cursor
                    draw_cursor(frame, cx, cy, telemetry["is_pinched"])
                    
                    # Package telemetry info for debugger panel
                    debug_info = {
                        "cx": cx,
                        "cy": cy,
                        "pinch_dist": telemetry["pinch_dist"],
                        "pinch_state": "Pinching" if telemetry["is_pinched"] else "Open",
                        "row": active_cell[0] if active_cell else ("None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen")),
                        "col": active_cell[1] if active_cell else ("None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen")),
                        "player": self.game.current_player
                    }
                else:
                    # Mouse coordinate hover mapping when hand is not in view
                    if self.game.game_over:
                        self.end_hovered_btn = check_end_button_hover(self.mouse_x, self.mouse_y)

                    # Default values for empty debug panel
                    debug_info = {
                        "cx": "None",
                        "cy": "None",
                        "pinch_dist": 0.0,
                        "pinch_state": "Open",
                        "row": "None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen"),
                        "col": "None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen"),
                        "player": self.game.current_player
                    }

                # 5. Render Board, Symbols, and active overlays
                draw_board(frame, self.game.board, active_cell)

                # 6. Render score board win tallies
                draw_scoreboard(frame, self.game.score)

                # 7. Draw winning path overlay line if a player aligned three
                if self.game.game_over and self.game.winner in ('X', 'O'):
                    draw_winning_line(frame, self.game.winning_line, self.win_line_progress)

                # 8. Render debug panel
                draw_debug_panel(frame, debug_info)

                # 9. Render Game Over overlay screen card
                if self.game.game_over:
                    draw_game_over_overlay(frame, self.game.winner, self.end_hovered_btn)

                # 10. Render game status text hud (turn indicator, handles "Computer Thinking...")
                draw_hud(frame, self.game.current_player, self.game.winner, self.game.game_over, self.ai_thinking)

                # 11. Calculate and render FPS
                current_time = time.time()
                time_diff = current_time - self.prev_time
                if time_diff <= 0:
                    time_diff = 0.001
                fps = 1.0 / time_diff
                self.prev_time = current_time

                # Draw top translucent overlay banner background
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (config.WIDTH, 70), (18, 18, 18), cv2.FILLED)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

                # Draw game active subtitle text
                hud_text = f"GAME ACTIVE | Mode: {self.difficulty} AI | R = Restart | ESC = Menu"
                (w, h), _ = cv2.getTextSize(hud_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.putText(
                    frame,
                    hud_text,
                    ((config.WIDTH - w) // 2, 42),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    config.COLOR_TEXT,
                    2,
                    cv2.LINE_AA
                )

                # Render dynamic FPS
                fps_text = f"FPS: {int(fps)}"
                (fps_w, fps_h), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.putText(
                    frame,
                    fps_text,
                    (config.WIDTH - fps_w - 20, 42),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

                cv2.imshow(config.WINDOW_NAME, frame)

                # 12. Keyboard event listener:
                # - 'R' / 'r' -> Restart match
                # - ESC (27) -> Return to main menu
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r') or key == ord('R'):
                    print("Shortcut 'R' pressed. Resetting board...")
                    self.game.reset()
                    self.win_line_progress = 0.0
                    self.end_hovered_btn = None
                    self.ai_thinking = False
                elif key == 27:  # ESC key
                    print("Shortcut 'ESC' pressed. Returning to menu...")
                    self.transition_to_menu()
                elif key == ord('q') or key == ord('Q'):
                    self.transition_to_menu()

        # Cleanup on exit
        self.cleanup()

    def cleanup(self):
        """Release all allocated resources cleanly."""
        print("Cleaning up application resources...")
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.detector is not None:
            self.detector.close()
            self.detector = None
        cv2.destroyAllWindows()
        print("Cleaned up successfully.")
