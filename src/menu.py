import cv2
import numpy as np
import config

def check_button_hover(mx, my):
    """
    Checks if the coordinates (mx, my) are inside the welcome screen buttons.
    Returns:
        "START" if hovering over Start Game.
        "DIFFICULTY" if hovering over Difficulty setting.
        "EXIT" if hovering over Exit.
        None otherwise.
    """
    x_min, y_min, x_max, y_max = config.BTN_START_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "START"

    x_min, y_min, x_max, y_max = config.BTN_DIFFICULTY_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "DIFFICULTY"

    x_min, y_min, x_max, y_max = config.BTN_EXIT_RECT
    if x_min <= mx <= x_max and y_min <= my <= y_max:
        return "EXIT"

    return None

def draw_menu(frame, hovered_btn=None, difficulty="Hard"):
    """
    Draws the welcome screen with Start Game, Difficulty, and Exit options.
    Parameters:
        frame: The OpenCV frame (numpy array) to draw on.
        hovered_btn: The button currently hovered ("START", "DIFFICULTY", "EXIT", or None).
        difficulty: The current AI difficulty string ("Easy", "Medium", or "Hard").
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

    # 3. Draw Start Game Button
    st_xmin, st_ymin, st_xmax, st_ymax = config.BTN_START_RECT
    is_start_hover = (hovered_btn == "START")
    start_bg = config.COLOR_BTN_HOVER if is_start_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (st_xmin, st_ymin), (st_xmax, st_ymax), start_bg, cv2.FILLED)
    cv2.rectangle(frame, (st_xmin, st_ymin), (st_xmax, st_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_start_text = "Start Game"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_start_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = st_xmin + (st_xmax - st_xmin - txt_w) // 2
    txt_y = st_ymin + (st_ymax - st_ymin + txt_h) // 2
    cv2.putText(frame, btn_start_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 4. Draw Difficulty Button
    df_xmin, df_ymin, df_xmax, df_ymax = config.BTN_DIFFICULTY_RECT
    is_diff_hover = (hovered_btn == "DIFFICULTY")
    diff_bg = config.COLOR_BTN_HOVER if is_diff_hover else config.COLOR_BTN_BG
    cv2.rectangle(frame, (df_xmin, df_ymin), (df_xmax, df_ymax), diff_bg, cv2.FILLED)
    cv2.rectangle(frame, (df_xmin, df_ymin), (df_xmax, df_ymax), config.COLOR_BTN_BORDER, 2)
    
    btn_diff_text = f"Difficulty: {difficulty}"
    (txt_w, txt_h), _ = cv2.getTextSize(btn_diff_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    txt_x = df_xmin + (df_xmax - df_xmin - txt_w) // 2
    txt_y = df_ymin + (df_ymax - df_ymin + txt_h) // 2
    cv2.putText(frame, btn_diff_text, (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 5. Draw Exit Button
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

    # 6. Draw Footer
    footer_text = "Hover mouse or hand cursor & pinch/click to select options."
    (ft_w, ft_h), _ = cv2.getTextSize(footer_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    ft_x = (config.WIDTH - ft_w) // 2
    cv2.putText(frame, footer_text, (ft_x, config.HEIGHT - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1, cv2.LINE_AA)
