"""
UI Rendering functions using OpenCV.
"""

import cv2
import numpy as np
import config

def draw_board(img, board, active_cell=None):
    """
    Draws the Tic-Tac-Toe grid, symbols, and hover overlays.
    """
    # 1. Draw Grid Lines
    # Vertical grid lines
    cv2.line(
        img,
        (config.BOARD_X_START + config.CELL_SIZE, config.BOARD_Y_START),
        (config.BOARD_X_START + config.CELL_SIZE, config.BOARD_Y_START + config.BOARD_SIZE),
        config.COLOR_GRID,
        6,
        cv2.LINE_AA
    )
    cv2.line(
        img,
        (config.BOARD_X_START + 2 * config.CELL_SIZE, config.BOARD_Y_START),
        (config.BOARD_X_START + 2 * config.CELL_SIZE, config.BOARD_Y_START + config.BOARD_SIZE),
        config.COLOR_GRID,
        6,
        cv2.LINE_AA
    )
    # Horizontal grid lines
    cv2.line(
        img,
        (config.BOARD_X_START, config.BOARD_Y_START + config.CELL_SIZE),
        (config.BOARD_X_START + config.BOARD_SIZE, config.BOARD_Y_START + config.CELL_SIZE),
        config.COLOR_GRID,
        6,
        cv2.LINE_AA
    )
    cv2.line(
        img,
        (config.BOARD_X_START, config.BOARD_Y_START + 2 * config.CELL_SIZE),
        (config.BOARD_X_START + config.BOARD_SIZE, config.BOARD_Y_START + 2 * config.CELL_SIZE),
        config.COLOR_GRID,
        6,
        cv2.LINE_AA
    )

    # 2. Draw Hover Cell Overlay (only if game is not over)
    if active_cell is not None:
        row, col = active_cell
        x1 = config.BOARD_X_START + col * config.CELL_SIZE
        y1 = config.BOARD_Y_START + row * config.CELL_SIZE
        x2 = x1 + config.CELL_SIZE
        y2 = y1 + config.CELL_SIZE
        
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), config.COLOR_HOVER, cv2.FILLED)
        cv2.addWeighted(overlay, 0.2, img, 0.8, 0, img)

    # 3. Draw Board Marks (X and O)
    for r in range(3):
        for c in range(3):
            mark = board[r][c]
            if mark == '':
                continue
            
            # Compute center of cell
            cx = config.BOARD_X_START + c * config.CELL_SIZE + config.CELL_SIZE // 2
            cy = config.BOARD_Y_START + r * config.CELL_SIZE + config.CELL_SIZE // 2
            
            if mark == 'X':
                size = 40
                cv2.line(img, (cx - size, cy - size), (cx + size, cy + size), config.COLOR_X, 10, cv2.LINE_AA)
                cv2.line(img, (cx + size, cy - size), (cx - size, cy + size), config.COLOR_X, 10, cv2.LINE_AA)
            elif mark == 'O':
                radius = 42
                cv2.circle(img, (cx, cy), radius, config.COLOR_O, 10, cv2.LINE_AA)

def draw_hud(img, current_player, winner, game_over, ai_thinking=False):
    """
    Draws game status texts, indicators, and buttons on the frame.
    """
    # Draw Turn Indicator below the board if game is active
    if not game_over:
        if ai_thinking:
            turn_text = "Computer Thinking..."
            txt_color = config.COLOR_O
        else:
            turn_text = f"Player Turn: {current_player}"
            txt_color = config.COLOR_X if current_player == 'X' else config.COLOR_O

        (w, h), _ = cv2.getTextSize(turn_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        text_x = (config.WIDTH - w) // 2
        text_y = config.BOARD_Y_START + config.BOARD_SIZE + 50
        
        # Outer capsule/bar background for turn text
        bar_padding_x = 25
        bar_padding_y = 10
        cv2.rectangle(
            img,
            (text_x - bar_padding_x, text_y - h - bar_padding_y),
            (text_x + w + bar_padding_x, text_y + bar_padding_y),
            (18, 18, 18),
            cv2.FILLED
        )
        cv2.rectangle(
            img,
            (text_x - bar_padding_x, text_y - h - bar_padding_y),
            (text_x + w + bar_padding_x, text_y + bar_padding_y),
            config.COLOR_GRID,
            1
        )
        
        cv2.putText(img, turn_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, txt_color, 2, cv2.LINE_AA)

def draw_cursor(img, cx, cy, is_clicking=False):
    """
    Draws a visual cursor at the hand pointer coordinates.
    """
    if is_clicking:
        cv2.circle(img, (cx, cy), 8, config.COLOR_SELECTION, cv2.FILLED, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 16, config.COLOR_SELECTION, 2, cv2.LINE_AA)
    else:
        cv2.circle(img, (cx, cy), 6, config.COLOR_CURSOR, cv2.FILLED, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 14, config.COLOR_CURSOR, 2, cv2.LINE_AA)

def draw_debug_panel(img, info):
    """
    Draws a semi-transparent panel with telemetry diagnostic details.
    """
    panel_x1, panel_y1 = 30, 110
    panel_x2, panel_y2 = 330, 410

    overlay = img.copy()
    cv2.rectangle(overlay, (panel_x1, panel_y1), (panel_x2, panel_y2), (20, 20, 20), cv2.FILLED)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)

    cv2.rectangle(img, (panel_x1, panel_y1), (panel_x2, panel_y2), config.COLOR_GRID, 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    line_height = 25
    x_offset = panel_x1 + 15
    y_offset = panel_y1 + 30

    cv2.putText(img, "TELEMETRY PANEL", (x_offset, y_offset), font, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(img, (x_offset, y_offset + 8), (panel_x2 - 15, y_offset + 8), config.COLOR_GRID, 1)
    
    y_offset += 40

    telemetry_data = [
        ("Fingertip Pos", f"({info.get('cx', 0)}, {info.get('cy', 0)})"),
        ("Pinch Dist", f"{info.get('pinch_dist', 0.0):.1f} px"),
        ("Pinch State", f"{info.get('pinch_state', 'Open')}", (0, 255, 255) if info.get('pinch_state') == 'Pinching' else (255, 255, 255)),
        ("Hover Cell", f"Row {info.get('row', 'None')}, Col {info.get('col', 'None')}"),
        ("Next Player", f"{info.get('player', 'X')}", config.COLOR_X if info.get('player') == 'X' else config.COLOR_O)
    ]

    for item in telemetry_data:
        label = item[0] + ":"
        value = item[1]
        val_color = item[2] if len(item) > 2 else (200, 200, 200)

        cv2.putText(img, label, (x_offset, y_offset), font, font_scale, (150, 150, 150), 1, cv2.LINE_AA)
        cv2.putText(img, value, (x_offset + 110, y_offset), font, font_scale, val_color, 1, cv2.LINE_AA)
        
        y_offset += line_height

def draw_scoreboard(img, score):
    """
    Draws a persistent scoreboard panel on the right side of the screen.
    """
    panel_x1, panel_y1 = 950, 110
    panel_x2, panel_y2 = 1250, 260

    # Background
    overlay = img.copy()
    cv2.rectangle(overlay, (panel_x1, panel_y1), (panel_x2, panel_y2), (20, 20, 20), cv2.FILLED)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)
    # Border
    cv2.rectangle(img, (panel_x1, panel_y1), (panel_x2, panel_y2), config.COLOR_GRID, 1)

    # Title
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "SCOREBOARD", (panel_x1 + 15, panel_y1 + 30), font, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(img, (panel_x1 + 15, panel_y1 + 38), (panel_x2 - 15, panel_y1 + 38), config.COLOR_GRID, 1)

    # Score content
    cv2.putText(img, f"Player X: {score['X']} wins", (panel_x1 + 15, panel_y1 + 75), font, 0.6, config.COLOR_X, 2, cv2.LINE_AA)
    cv2.putText(img, f"Player O: {score['O']} wins", (panel_x1 + 15, panel_y1 + 120), font, 0.6, config.COLOR_O, 2, cv2.LINE_AA)

def draw_winning_line(img, winning_line, progress):
    """
    Draws a gold win-line intersecting the center of three winning cells, growing dynamically.
    """
    if winning_line is None or progress <= 0:
        return

    line_type, idx = winning_line
    
    # Compute base endpoints in pixel dimensions
    if line_type == 'row':
        y = config.BOARD_Y_START + idx * config.CELL_SIZE + config.CELL_SIZE // 2
        x1 = config.BOARD_X_START + 15
        x2 = config.BOARD_X_START + config.BOARD_SIZE - 15
        y1, y2 = y, y
    elif line_type == 'col':
        x = config.BOARD_X_START + idx * config.CELL_SIZE + config.CELL_SIZE // 2
        y1 = config.BOARD_Y_START + 15
        y2 = config.BOARD_Y_START + config.BOARD_SIZE - 15
        x1, x2 = x, x
    elif line_type == 'diag':
        if idx == 0:  # Main Diagonal
            x1 = config.BOARD_X_START + 20
            y1 = config.BOARD_Y_START + 20
            x2 = config.BOARD_X_START + config.BOARD_SIZE - 20
            y2 = config.BOARD_Y_START + config.BOARD_SIZE - 20
        else:  # Anti Diagonal
            x1 = config.BOARD_X_START + config.BOARD_SIZE - 20
            y1 = config.BOARD_Y_START + 20
            x2 = config.BOARD_X_START + 20
            y2 = config.BOARD_Y_START + config.BOARD_SIZE - 20
    else:
        return

    # Apply growth progress animation
    curr_x2 = int(x1 + progress * (x2 - x1))
    curr_y2 = int(y1 + progress * (y2 - y1))

    # Draw gold indicator win line
    cv2.line(img, (x1, y1), (curr_x2, curr_y2), config.COLOR_WIN_LINE, 10, cv2.LINE_AA)

def draw_game_over_overlay(img, winner, hovered_btn=None):
    """
    Draws the Game Over overlay card containing result message and action buttons.
    """
    if winner is None:
        return

    # Overlay card dimension constants
    card_x1, card_y1 = 390, 210
    card_x2, card_y2 = 890, 510

    # Draw card box with high transparency overlay (dim background)
    overlay = img.copy()
    cv2.rectangle(overlay, (card_x1, card_y1), (card_x2, card_y2), (15, 15, 15), cv2.FILLED)
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)
    # Border
    cv2.rectangle(img, (card_x1, card_y1), (card_x2, card_y2), config.COLOR_GRID, 2)

    # 1. Display Header Result Message
    font = cv2.FONT_HERSHEY_DUPLEX
    if winner == 'Draw':
        msg = "GAME DRAW!"
        color = (240, 240, 240)
    else:
        msg = f"PLAYER {winner} WINS!"
        color = config.COLOR_X if winner == 'X' else config.COLOR_O

    (w, h), _ = cv2.getTextSize(msg, font, 0.9, 2)
    cv2.putText(img, msg, (card_x1 + (500 - w) // 2, card_y1 + 80), font, 0.9, color, 2, cv2.LINE_AA)

    # 2. Draw Play Again Button
    p_xmin, p_ymin, p_xmax, p_ymax = config.BTN_PLAY_RECT
    is_p_hover = (hovered_btn == "PLAY")
    p_bg = config.COLOR_BTN_HOVER if is_p_hover else config.COLOR_BTN_BG
    cv2.rectangle(img, (p_xmin, p_ymin), (p_xmax, p_ymax), p_bg, cv2.FILLED)
    cv2.rectangle(img, (p_xmin, p_ymin), (p_xmax, p_ymax), config.COLOR_BTN_BORDER, 2)
    
    p_text = "Play Again"
    (pw, ph), _ = cv2.getTextSize(p_text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    cv2.putText(img, p_text, (p_xmin + (200 - pw) // 2, p_ymin + (60 + ph) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.65, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

    # 3. Draw Main Menu Button
    m_xmin, m_ymin, m_xmax, m_ymax = config.BTN_MENU_RECT
    is_m_hover = (hovered_btn == "MENU_BTN")
    m_bg = config.COLOR_BTN_EXIT_HOVER if is_m_hover else config.COLOR_BTN_BG
    cv2.rectangle(img, (m_xmin, m_ymin), (m_xmax, m_ymax), m_bg, cv2.FILLED)
    cv2.rectangle(img, (m_xmin, m_ymin), (m_xmax, m_ymax), config.COLOR_BTN_BORDER, 2)

    m_text = "Main Menu"
    (mw, mh), _ = cv2.getTextSize(m_text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    cv2.putText(img, m_text, (m_xmin + (200 - mw) // 2, m_ymin + (60 + mh) // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.65, config.COLOR_BTN_TEXT, 2, cv2.LINE_AA)

def check_end_button_hover(mx, my):
    """
    Hit-testing to verify if coordinates (mx, my) lie over the Game Over card buttons.
    Returns:
        "PLAY" if hovering over Play Again.
        "MENU_BTN" if hovering over Main Menu.
        None otherwise.
    """
    p_xmin, p_ymin, p_xmax, p_ymax = config.BTN_PLAY_RECT
    if p_xmin <= mx <= p_xmax and p_ymin <= my <= p_ymax:
        return "PLAY"

    m_xmin, m_ymin, m_xmax, m_ymax = config.BTN_MENU_RECT
    if m_xmin <= mx <= m_xmax and m_ymin <= my <= m_ymax:
        return "MENU_BTN"

    return None
