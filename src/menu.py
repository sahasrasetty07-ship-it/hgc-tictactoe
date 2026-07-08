import cv2
import numpy as np
import config

def check_button_hover(mx, my):
    """
    Checks if the coordinates (mx, my) are inside the welcome screen buttons.
    Returns:
        "PLAY_AI" if hovering over Play vs AI.
        "PLAY_FRIEND" if hovering over Play with Friend.
        "DIFFICULTY" if hovering over Difficulty setting.
        "P1_NAME" if hovering over Player 1 Name field.
        "P2_NAME" if hovering over Player 2 Name field.
        "EXIT" if hovering over Exit.
        None otherwise.
    """
    x_min, y_min, x_max, y_max = config.BTN_PLAY_AI_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "PLAY_AI"

    x_min, y_min, x_max, y_max = config.BTN_PLAY_FRIEND_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "PLAY_FRIEND"

    x_min, y_min, x_max, y_max = config.BTN_DIFFICULTY_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "DIFFICULTY"

    x_min, y_min, x_max, y_max = config.BTN_P1_NAME_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "P1_NAME"

    x_min, y_min, x_max, y_max = config.BTN_P2_NAME_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "P2_NAME"

    x_min, y_min, x_max, y_max = config.BTN_EXIT_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "EXIT"

    return None

def draw_menu(frame, hovered_btn=None, difficulty="Hard", p1_name="", p2_name="", active_input=None):
    """
    Draws the welcome screen with Start Game, Difficulty, and Exit options.
    Parameters:
        frame: The OpenCV frame (numpy array) to draw on.
        hovered_btn: The button currently hovered ("PLAY_AI", "PLAY_FRIEND", "DIFFICULTY", "P1_NAME", "P2_NAME", "EXIT", or None).
        difficulty: The current AI difficulty string ("Easy", "Medium", or "Hard").
        p1_name: Player 1 nickname string.
        p2_name: Player 2 nickname string.
        active_input: The currently active name input field ("PLAYER1", "PLAYER2", or None).
    """
    # 1. Clear frame with background color
    frame[:] = config.COLOR_BG

    # 2. Draw modern Title Header
    title_text = "TIC-TAC-TOE"
    subtitle_text = "Hand Gesture Controlled Edition"
    
    # Calculate text sizes for centering
    (title_w, title_h), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_DUPLEX, 1.8, 3)
    (sub_w, sub_h), _ = cv2.getTextSize(subtitle_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    
    title_x = (config.WIDTH - title_w) // 2
    sub_x = (config.WIDTH - sub_w) // 2
    
    cv2.putText(frame, title_text, (title_x, 130), cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(frame, subtitle_text, (sub_x, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_HOVER, 1, cv2.LINE_AA)

    # 3. Draw Play vs AI Button
    ai_xmin, ai_ymin, ai_xmax, ai_ymax = config.BTN_PLAY_AI_RECT
    is_ai_hover = (hovered_btn == "PLAY_AI")
    ai_bg = config.COLOR_BTN_HOVER if is_ai_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (ai_xmin, ai_ymin), (ai_xmax, ai_ymax), ai_bg, cv2.FILLED)
    cv2.rectangle(frame, (ai_xmin, ai_ymin), (ai_xmax, ai_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_ai_text = "Play vs AI"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_ai_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = ai_xmin + (ai_xmax - ai_xmin - txt_w) // 2
    txt_y = ai_ymin + (ai_ymax - ai_ymin + txt_h) // 2
    cv2.putText(frame, btn_ai_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 4. Draw Play with Friend Button
    fr_xmin, fr_ymin, fr_xmax, fr_ymax = config.BTN_PLAY_FRIEND_RECT
    is_fr_hover = (hovered_btn == "PLAY_FRIEND")
    fr_bg = config.COLOR_BTN_HOVER if is_fr_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (fr_xmin, fr_ymin), (fr_xmax, fr_ymax), fr_bg, cv2.FILLED)
    cv2.rectangle(frame, (fr_xmin, fr_ymin), (fr_xmax, fr_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_fr_text = "Play with Friend"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_fr_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = fr_xmin + (fr_xmax - fr_xmin - txt_w) // 2
    txt_y = fr_ymin + (fr_ymax - fr_ymin + txt_h) // 2
    cv2.putText(frame, btn_fr_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 5. Draw Difficulty Button
    df_xmin, df_ymin, df_xmax, df_ymax = config.BTN_DIFFICULTY_RECT
    is_diff_hover = (hovered_btn == "DIFFICULTY")
    diff_bg = config.COLOR_BTN_HOVER if is_diff_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (df_xmin, df_ymin), (df_xmax, df_ymax), diff_bg, cv2.FILLED)
    cv2.rectangle(frame, (df_xmin, df_ymin), (df_xmax, df_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_diff_text = f"AI Difficulty: {difficulty}"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_diff_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = df_xmin + (df_xmax - df_xmin - txt_w) // 2
    txt_y = df_ymin + (df_ymax - df_ymin + txt_h) // 2
    cv2.putText(frame, btn_diff_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 6. Draw Player 1 input field
    p1_xmin, p1_ymin, p1_xmax, p1_ymax = config.BTN_P1_NAME_RECT
    is_p1_active = (active_input == "PLAYER1")
    is_p1_hover = (hovered_btn == "P1_NAME")
    p1_border = config.COLOR_SELECTION if is_p1_active else (config.COLOR_BTN_HOVER if is_p1_hover else config.COLOR_BTN_BORDER)
    cv2.rectangle(frame, (p1_xmin, p1_ymin), (p1_xmax, p1_ymax), config.COLOR_BTN_BG, cv2.FILLED)
    cv2.rectangle(frame, (p1_xmin, p1_ymin), (p1_xmax, p1_ymax), p1_border, 2 if is_p1_active else 1)
    
    cv2.putText(frame, "Player 1 (X) Name:", (p1_xmin, p1_ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_TEXT, 1, cv2.LINE_AA)
    
    display_p1 = p1_name + ("|" if is_p1_active else "")
    if p1_name == "":
        display_p1 = "Player 1 (Default)"
        txt_color = (120, 120, 120)
    else:
        txt_color = config.COLOR_TEXT
    
    (txt_w, txt_h), _ = cv2.getTextSize(display_p1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    cv2.putText(frame, display_p1, (p1_xmin + 15, p1_ymin + (p1_ymax - p1_ymin + txt_h) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, txt_color, 1, cv2.LINE_AA)

    # 7. Draw Player 2 input field
    p2_xmin, p2_ymin, p2_xmax, p2_ymax = config.BTN_P2_NAME_RECT
    is_p2_active = (active_input == "PLAYER2")
    is_p2_hover = (hovered_btn == "P2_NAME")
    p2_border = config.COLOR_SELECTION if is_p2_active else (config.COLOR_BTN_HOVER if is_p2_hover else config.COLOR_BTN_BORDER)
    cv2.rectangle(frame, (p2_xmin, p2_ymin), (p2_xmax, p2_ymax), config.COLOR_BTN_BG, cv2.FILLED)
    cv2.rectangle(frame, (p2_xmin, p2_ymin), (p2_xmax, p2_ymax), p2_border, 2 if is_p2_active else 1)
    
    cv2.putText(frame, "Player 2 (O) Name:", (p2_xmin, p2_ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.COLOR_TEXT, 1, cv2.LINE_AA)
    
    display_p2 = p2_name + ("|" if is_p2_active else "")
    if p2_name == "":
        display_p2 = "Player 2 (Default)"
        txt_color = (120, 120, 120)
    else:
        txt_color = config.COLOR_TEXT
    
    (txt_w, txt_h), _ = cv2.getTextSize(display_p2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    cv2.putText(frame, display_p2, (p2_xmin + 15, p2_ymin + (p2_ymax - p2_ymin + txt_h) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, txt_color, 1, cv2.LINE_AA)

    # 8. Draw Exit Button
    ex_xmin, ex_ymin, ex_xmax, ex_ymax = config.BTN_EXIT_RECT
    is_exit_hover = (hovered_btn == "EXIT")
    exit_bg = config.COLOR_BTN_EXIT_HOVER if is_exit_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (ex_xmin, ex_ymin), (ex_xmax, ex_ymax), exit_bg, cv2.FILLED)
    cv2.rectangle(frame, (ex_xmin, ex_ymin), (ex_xmax, ex_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_exit_text = "Exit"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_exit_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = ex_xmin + (ex_xmax - ex_xmin - txt_w) // 2
    txt_y = ex_ymin + (ex_ymax - ex_ymin + txt_h) // 2
    cv2.putText(frame, btn_exit_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 9. Draw Footer
    footer_text = "Hover mouse & click options. Click a Player text box to type nickname."
    (ft_w, ft_h), _ = cv2.getTextSize(footer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    ft_x = (config.WIDTH - ft_w) // 2
    cv2.putText(frame, footer_text, (ft_x, config.HEIGHT - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1, cv2.LINE_AA)
