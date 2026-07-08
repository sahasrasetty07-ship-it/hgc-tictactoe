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
        
        # Game mode selection ("AI" or "PVP")
        self.game_mode = "AI"
        
        # Player Nicknames and active input text box state
        self.p1_name = ""
        self.p2_name = ""
        self.active_input = None
        self.game_over_time = None
        
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
                if self.hovered_btn == "PLAY_AI":
                    self.game_mode = "AI"
                    self.transition_to_game()
                elif self.hovered_btn == "PLAY_FRIEND":
                    self.game_mode = "PVP"
                    self.transition_to_game()
                elif self.hovered_btn == "DIFFICULTY":
                    self._cycle_difficulty()
                elif self.hovered_btn == "P1_NAME":
                    self.active_input = "PLAYER1"
                elif self.hovered_btn == "P2_NAME":
                    self.active_input = "PLAYER2"
                elif self.hovered_btn == "EXIT":
                    print("Exit button clicked.")
                    self.running = False
                else:
                    # Deselect name inputs if clicking elsewhere
                    self.active_input = None
        
        elif self.state == config.STATE_GAME:
            # Check for game over button hovers and clicks only after delay has expired
            if self.game.game_over:
                if self.game_over_time is not None and time.time() - self.game_over_time >= config.GAME_OVER_DELAY:
                    self.end_hovered_btn = check_end_button_hover(x, y)
                    if event == cv2.EVENT_LBUTTONDOWN:
                        if self.end_hovered_btn == "PLAY":
                            print("Mouse clicked Play Again.")
                            self.game.reset()
                            self.game_over_time = None
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
        self.game_over_time = None
        
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
                draw_menu(menu_frame, self.hovered_btn, self.difficulty, self.p1_name, self.p2_name, self.active_input)
                
                # Check for hand inputs in menu state
                if self.detector is not None:
                    # Normally webcam is off in menu, but if detector exists we can query it
                    pass
                
                cv2.imshow(config.WINDOW_NAME, menu_frame)
                
                # 2. Key input:
                key = cv2.waitKey(33)
                if key != -1:
                    ascii_key = key & 0xFF
                    if self.active_input is not None:
                        if ascii_key in (8, 127): # Backspace
                            if self.active_input == "PLAYER1":
                                self.p1_name = self.p1_name[:-1]
                            elif self.active_input == "PLAYER2":
                                self.p2_name = self.p2_name[:-1]
                        elif ascii_key in (10, 13, 27): # Enter or Escape
                            self.active_input = None
                        elif 32 <= ascii_key <= 126: # Printable characters
                            char = chr(ascii_key)
                            if self.active_input == "PLAYER1" and len(self.p1_name) < 12:
                                self.p1_name += char
                            elif self.active_input == "PLAYER2" and len(self.p2_name) < 12:
                                self.p2_name += char
                    else:
                        if ascii_key == ord('q') or ascii_key == ord('Q') or ascii_key == 27:
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

                # 2. Handle AI Thinking State Machine (Automatic turn for O in AI mode)
                if self.game_mode == "AI" and not self.game.game_over and self.game.current_player == 'O':
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

                # 3. Track game over timestamp and increment winning line animation progress if win occurred
                if self.game.game_over:
                    if self.game_over_time is None:
                        self.game_over_time = time.time()
                    
                    if self.game.winner in ('X', 'O'):
                        if self.win_line_progress < 1.0:
                            self.win_line_progress = min(1.0, self.win_line_progress + 0.05)

                # 4. Detect hand, get interaction telemetry
                telemetry = self.detector.process_interaction(frame, timestamp_ms, game_mode=self.game_mode, draw=True)

                # Active grid cell selection tracking
                active_cell = None
                
                # Check for inputs
                current_p = self.game.current_player
                active_telemetry = telemetry.get(current_p) if (telemetry and current_p in telemetry) else None
                
                if not self.game.game_over and not self.ai_thinking:
                    if active_telemetry is not None:
                        cx, cy = active_telemetry["cx"], active_telemetry["cy"]
                        
                        # 4a. Map cursor position to grid cell (row, col)
                        if (config.BOARD_X_START <= cx < config.BOARD_X_START + config.BOARD_SIZE) and \
                           (config.BOARD_Y_START <= cy < config.BOARD_Y_START + config.BOARD_SIZE):
                            col = (cx - config.BOARD_X_START) // config.CELL_SIZE
                            row = (cy - config.BOARD_Y_START) // config.CELL_SIZE
                            
                            row = max(0, min(2, row))
                            col = max(0, min(2, col))
                            active_cell = (row, col)
                        
                        # 4b. Handle grid click triggers
                        if active_telemetry["click_triggered"] and active_cell is not None:
                            success_move = self.game.make_move(row, col)
                            if success_move:
                                print(f"Placed mark at Row {row}, Col {col}. Next turn: {self.game.current_player}")
                    
                elif self.game.game_over:
                    # If game is over and the delay has passed, allow either player to click the menu buttons
                    if self.game_over_time is not None and time.time() - self.game_over_time >= config.GAME_OVER_DELAY:
                        button_clicked = False
                        for p in ['X', 'O']:
                            p_tel = telemetry.get(p) if telemetry else None
                            if p_tel is not None:
                                cx, cy = p_tel["cx"], p_tel["cy"]
                                self.end_hovered_btn = check_end_button_hover(cx, cy)
                                if p_tel["click_triggered"] and self.end_hovered_btn is not None:
                                    if self.end_hovered_btn == "PLAY":
                                        print(f"Player {p} pinch triggered Play Again.")
                                        self.game.reset()
                                        self.game_over_time = None
                                        self.win_line_progress = 0.0
                                        self.end_hovered_btn = None
                                        button_clicked = True
                                        break
                                    elif self.end_hovered_btn == "MENU_BTN":
                                        print(f"Player {p} pinch triggered Main Menu.")
                                        self.transition_to_menu()
                                        button_clicked = True
                                        break
                        
                        # Mouse fallback for game over buttons
                        if not button_clicked:
                            self.end_hovered_btn = check_end_button_hover(self.mouse_x, self.mouse_y)

                # Render passive/active cursors for any detected hands
                if telemetry is not None:
                    for p, tel in telemetry.items():
                        cursor_color = config.COLOR_X if p == 'X' else config.COLOR_O
                        draw_cursor(frame, tel["cx"], tel["cy"], tel["is_pinched"], cursor_color)
                    
                # Package telemetry info for debugger panel
                if active_telemetry is not None:
                    debug_info = {
                        "cx": active_telemetry["cx"],
                        "cy": active_telemetry["cy"],
                        "pinch_dist": active_telemetry["pinch_dist"],
                        "pinch_state": "Pinching" if active_telemetry["is_pinched"] else "Open",
                        "row": active_cell[0] if active_cell else ("None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen")),
                        "col": active_cell[1] if active_cell else ("None" if not self.game.game_over and not self.ai_thinking else ("Thinking" if self.ai_thinking else "Frozen")),
                        "player": self.game.current_player
                    }
                else:
                    # Mouse coordinate hover mapping when hand is not in view
                    if self.game.game_over and self.game_over_time is not None and time.time() - self.game_over_time >= config.GAME_OVER_DELAY:
                        self.end_hovered_btn = check_end_button_hover(self.mouse_x, self.mouse_y)

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
                draw_board(frame, self.game.board, active_cell, self.game.winning_line)

                # 6. Render score board win tallies
                p1_display = self.p1_name.strip() if self.p1_name.strip() != "" else "Player 1"
                p2_display = self.p2_name.strip() if (self.p2_name.strip() != "" and self.game_mode == "PVP") else ("AI" if self.game_mode == "AI" else "Player 2")
                draw_scoreboard(frame, self.game.score, p1_display, p2_display)

                # 7. Draw winning path overlay line if a player aligned three
                if self.game.game_over and self.game.winner in ('X', 'O'):
                    draw_winning_line(frame, self.game.winning_line, self.win_line_progress)

                # 8. Render debug panel
                draw_debug_panel(frame, debug_info)

                # 9. Render Game Over overlay screen card (only after delay)
                show_game_over = False
                if self.game.game_over and self.game_over_time is not None:
                    if time.time() - self.game_over_time >= config.GAME_OVER_DELAY:
                        show_game_over = True
                
                if show_game_over:
                    draw_game_over_overlay(frame, self.game.winner, p1_display, p2_display, self.end_hovered_btn)

                # 10. Render game status text hud (turn indicator, handles "Computer Thinking...")
                draw_hud(frame, self.game.current_player, p1_display, p2_display, self.game.winner, self.game.game_over, self.ai_thinking)

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
                mode_str = "vs Friend" if self.game_mode == "PVP" else f"{self.difficulty} AI"
                hud_text = f"GAME ACTIVE | Mode: {mode_str} | R = Restart | ESC = Menu"
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
                    self.game_over_time = None
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
