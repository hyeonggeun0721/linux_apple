import tkinter as tk
import random
import time
import socket       # [추가] 통신용
import threading    # [추가] 비동기 수신용

# ================================
# [설정] 네트워크 전역 변수
# ================================
CLIENT_SOCKET = None
# ★ 학교 서버 IP (만약 맥북에서 서버를 켠다면 "127.0.0.1"로 변경하세요)
SERVER_IP = "10.125.234.111" 
SERVER_PORT = 8080

# ================================
# Game 클래스: 게임 상태 관리
# ================================
class Game:
    def __init__(self, board_data_param, first_player_is_human=True):
        self.board = board_data_param   # 게임 보드 (숫자)
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        # owner_board: 'none', 'human', 'ai'
        self.owner_board = [['none' for _ in range(self.cols)] for _ in range(self.rows)]
        self.player_scores = {"human": 0, "ai": 0}
        self.current_turn = "human" if first_player_is_human else "ai"
        self.consecutive_passes = 0
        self.game_over = False

    def isValid(self, r1, c1, r2, c2):
        # 클라이언트에서는 이제 이 함수를 직접 호출해 판정하지 않지만,
        # 드래그 시각 효과(초록/빨강)를 위해 남겨둡니다.
        sums = 0
        if not (0 <= r1 <= r2 < self.rows and 0 <= c1 <= c2 < self.cols):
            return False
        all_zero = True
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if self.board[r][c] != 0:
                    all_zero = False
                    sums += self.board[r][c]
        if all_zero: return False
        return sums == 10

    def calculateMove(self): 
        # AI 로직 (현재 클라이언트에서는 사용 안 함, 추후 AI 봇 모드용)
        return (-1, -1, -1, -1)

    def process_move(self, r1, c1, r2, c2, player_type):
        # 이제 이 함수는 서버 응답을 받았을 때만 실행됩니다.
        if self.game_over: return None
        
        cells_to_animate = []
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if self.board[r][c] != 0:
                    self.board[r][c] = 0 # 보드 지우기
                    cells_to_animate.append((r, c))
        return cells_to_animate 

    def switch_turn(self):
        self.current_turn = "ai" if self.current_turn == "human" else "human"
        update_canvas_cursor()
        update_score_display()

    def check_game_over(self):
        if self.consecutive_passes >= 2:
            self.game_over = True
            update_canvas_cursor()
            update_score_display()
            display_game_over_message()
            return True
        return False

# ================================
# Tkinter GUI 설정 및 전역 변수
# ================================
NUM_ROWS = 10
NUM_COLS = 17
CELL_SIZE = 40
FONT_SIZE = 16
SCOREBOARD_WIDTH = 250
WINDOW_WIDTH = NUM_COLS * CELL_SIZE + (SCOREBOARD_WIDTH * 2) + 20
WINDOW_HEIGHT = NUM_ROWS * CELL_SIZE + 180

root = tk.Tk()
root.title("Net-Mushroom Client")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.config(bg="white")

# 레이아웃 설정
root.grid_rowconfigure(0, weight=0, minsize=50)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)
root.grid_columnconfigure(2, weight=1)

main_game_frame = tk.Frame(root, bg="white")
main_game_frame.grid(row=1, column=0, columnspan=3, pady=5)

# --- 점수판 (좌측: Human) ---
human_score_frame = tk.Frame(main_game_frame, bd=0, relief="flat", bg="white")
human_score_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
human_info_bg_frame = tk.Frame(human_score_frame, bd=0, relief="flat")
human_info_bg_frame.pack(fill="both", expand=True)
human_emoji_label = tk.Label(human_info_bg_frame, text="😊", font=("Arial", 45, "bold"))
human_emoji_label.pack(pady=(10,0))
human_name_label = tk.Label(human_info_bg_frame, text="플레이어", font=("Arial", 20, "normal"))
human_name_label.pack()
human_score_label = tk.Label(human_score_frame, text="0", font=("Arial", 45, "bold"), bg="white")
human_score_label.pack(pady=(0,10))

# --- 게임 보드 (중앙) ---
game_board_frame = tk.Frame(main_game_frame, bd=2, relief="sunken", bg="white")
game_board_frame.grid(row=0, column=1, padx=10, pady=5)
canvas = tk.Canvas(game_board_frame, width=NUM_COLS * CELL_SIZE, height=NUM_ROWS * CELL_SIZE, bg="white", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# --- 점수판 (우측: AI/Opponent) ---
ai_score_frame = tk.Frame(main_game_frame, bd=0, relief="flat", bg="white")
ai_score_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
ai_info_bg_frame = tk.Frame(ai_score_frame, bd=0, relief="flat")
ai_info_bg_frame.pack(fill="both", expand=True)
ai_emoji_label = tk.Label(ai_info_bg_frame, text="🤖", font=("Arial", 45, "bold"))
ai_emoji_label.pack(pady=(10,0))
ai_name_label = tk.Label(ai_info_bg_frame, text="상대방", font=("Arial", 20, "normal"))
ai_name_label.pack()
ai_score_label = tk.Label(ai_score_frame, text="0", font=("Arial", 45, "bold"), bg="white")
ai_score_label.pack(pady=(0,10))

# --- 버튼 프레임 ---
button_frame = tk.Frame(root, bg="white")
button_frame.grid(row=2, column=0, columnspan=3, pady=(5,15))

reset_button = tk.Button(button_frame, text="다시 하기", command=lambda: initialize_game(True), width=12, height=2)
reset_button.pack(side=tk.LEFT, padx=5)
pass_button = tk.Button(button_frame, text="스킵", command=lambda: handle_pass(), width=12, height=2)
pass_button.pack(side=tk.LEFT, padx=5)
connect_btn = tk.Button(button_frame, text="서버 연결", command=lambda: connect_to_server(), bg="yellow", width=12, height=2)
connect_btn.pack(side=tk.LEFT, padx=5)
test_msg_btn = tk.Button(button_frame, text="인사 보내기", command=lambda: send_test_message(), bg="lightgreen", width=12, height=2)
test_msg_btn.pack(side=tk.LEFT, padx=5)

# --- 전역 변수 ---
current_game = None
start_x, start_y = -1, -1
current_rect_id = None
thinking_text_id = None
game_over_text_id = None
animation_queue = []
animation_target_color = ""

# ================================
# [핵심] 네트워크 함수
# ================================
def connect_to_server():
    global CLIENT_SOCKET
    try:
        CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CLIENT_SOCKET.connect((SERVER_IP, SERVER_PORT))
        print(f"서버({SERVER_IP}:{SERVER_PORT})에 연결되었습니다!")
        
        # 수신 스레드 시작
        recv_thread = threading.Thread(target=receive_message, daemon=True)
        recv_thread.start()
        
    except Exception as e:
        print(f"서버 연결 실패: {e}")

def receive_message():
    """서버로부터 메시지를 수신하고 처리하는 함수"""
    global CLIENT_SOCKET, current_game
    while True:
        try:
            data = CLIENT_SOCKET.recv(1024)
            if not data:
                print("서버와 연결이 끊어졌습니다.")
                break
            
            msg = data.decode('utf-8')
            print(f"[서버 수신]: {msg}")
            
            # --- 프로토콜 파싱 ---
            parts = msg.split()
            command = parts[0]

            if command == "VALID":
                # 서버: "VALID r1 c1 r2 c2 score"
                # 정답이므로 해당 영역을 지우고 점수 갱신
                r1, c1, r2, c2 = map(int, parts[1:5])
                new_score = int(parts[5])

                # 1. 보드 데이터 0으로 갱신
                cells_to_animate = []
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        if current_game.board[r][c] != 0:
                            current_game.board[r][c] = 0
                            cells_to_animate.append((r, c))
                
                # 2. 점수 갱신
                current_game.player_scores['human'] = new_score
                
                # 3. 애니메이션 실행 (메인 스레드 UI 갱신 요청)
                # Tkinter는 원칙적으로 메인 스레드에서만 GUI를 건드려야 하지만, 
                # 간단한 작업은 여기서 호출해도 작동하는 경우가 많음. 
                # (엄격하게 하려면 queue나 after 사용 필요)
                _animate_cell_fill(cells_to_animate, "human")

            elif command == "INVALID":
                print("서버: 잘못된 이동입니다.")

        except Exception as e:
            print(f"수신 오류: {e}")
            break

def send_test_message():
    if CLIENT_SOCKET:
        try:
            CLIENT_SOCKET.send("Hello Server!".encode('utf-8'))
        except:
            print("전송 실패")

# ================================
# GUI 그리기 함수
# ================================
def get_cell_coords(event_x, event_y):
    r = event_y // CELL_SIZE
    c = event_x // CELL_SIZE
    return r, c

def draw_board():
    canvas.delete("all")
    if not current_game: return
    for r in range(current_game.rows):
        for c in range(current_game.cols):
            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            bg_color = "white"
            # 소유권 색상 표시
            if current_game.owner_board[r][c] == 'human':
                bg_color = "lightblue"
            elif current_game.owner_board[r][c] == 'ai':
                bg_color = "lightcoral"
            
            canvas.create_rectangle(x1, y1, x2, y2, outline="gray", width=1, fill=bg_color)
            
            number = current_game.board[r][c]
            if number != 0:
                canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2,
                                   text=str(number), font=("Arial", FONT_SIZE, "bold"), fill="black")
    update_score_display()

def update_score_display():
    if not current_game: return
    human_score_label.config(text=f"{current_game.player_scores['human']}")
    ai_score_label.config(text=f"{current_game.player_scores['ai']}")
    
    # 턴 표시 색상 변경
    if current_game.current_turn == "human":
        set_info_frame_colors(human_info_bg_frame, "lightblue")
        set_info_frame_colors(ai_info_bg_frame, "white")
    else:
        set_info_frame_colors(human_info_bg_frame, "white")
        set_info_frame_colors(ai_info_bg_frame, "lightpink")

def set_info_frame_colors(info_frame, color):
    info_frame.config(bg=color)
    for widget in info_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=color)

def draw_selection_rectangle(x1, y1, x2, y2, color="black"):
    global current_rect_id
    if current_rect_id:
        canvas.delete(current_rect_id)
    current_rect_id = canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, dash=(7, 7))

def clear_selection_rectangle():
    global current_rect_id
    if current_rect_id:
        canvas.delete(current_rect_id)
        current_rect_id = None

def display_game_over_message():
    global game_over_text_id
    if game_over_text_id: canvas.delete(game_over_text_id)
    
    h_score = current_game.player_scores['human']
    a_score = current_game.player_scores['ai']
    winner = "플레이어 승!" if h_score > a_score else "상대방 승!" if a_score > h_score else "무승부"
    
    msg = f"게임 종료! {winner}\n({h_score} vs {a_score})"
    game_over_text_id = canvas.create_text(
        NUM_COLS * CELL_SIZE / 2, NUM_ROWS * CELL_SIZE / 2,
        text=msg, font=("Arial", 24, "bold"), fill="red", justify=tk.CENTER
    )

def update_canvas_cursor():
    if current_game and current_game.current_turn == "human":
        canvas.config(cursor="cross")
    else:
        canvas.config(cursor="arrow")

def _animate_cell_fill(cells, player_type):
    global animation_queue, animation_target_color
    animation_queue = list(cells)
    animation_target_color = "lightblue" if player_type == "human" else "lightcoral"
    update_score_display()
    _animate_next_cell()

def _animate_next_cell():
    global animation_queue, animation_target_color
    if animation_queue:
        r, c = animation_queue.pop(0)
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        
        # 셀 배경색 변경 (숫자는 유지)
        canvas.create_rectangle(x1, y1, x2, y2, outline="gray", width=1, fill=animation_target_color)
        
        # 숫자 다시 그리기 (0이면 안 그림)
        if current_game.board[r][c] != 0:
             canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2,
                                text=str(current_game.board[r][c]), font=("Arial", FONT_SIZE, "bold"), fill="black")

        root.after(50, _animate_next_cell)
    else:
        # 애니메이션 끝나면 턴 넘기기 등의 후처리 가능
        pass

# ================================
# 이벤트 핸들러
# ================================
def on_canvas_press(event):
    global start_x, start_y
    if not current_game or current_game.game_over: return
    start_x, start_y = event.x, event.y
    clear_selection_rectangle()

def on_canvas_drag(event):
    if not current_game or current_game.game_over or start_x == -1: return
    
    end_x = max(0, min(event.x, NUM_COLS * CELL_SIZE - 1))
    end_y = max(0, min(event.y, NUM_ROWS * CELL_SIZE - 1))
    
    # 드래그 영역 시각화
    r1, c1 = get_cell_coords(start_x, start_y)
    r2, c2 = get_cell_coords(end_x, end_y)
    
    # 유효성 검사 시각화 (초록/빨강) - 클라이언트 측 힌트
    color = "red"
    if current_game.isValid(min(r1,r2), min(c1,c2), max(r1,r2), max(c1,c2)):
        color = "light green"
        
    draw_selection_rectangle(start_x, start_y, end_x, end_y, color)

def on_canvas_release(event):
    global start_x, start_y, CLIENT_SOCKET
    if not current_game or current_game.game_over or start_x == -1:
        start_x, start_y = -1, -1
        return

    # 1. 좌표 계산
    r1, c1 = get_cell_coords(start_x, start_y)
    r2, c2 = get_cell_coords(event.x, event.y)
    
    fr1, fr2 = min(r1, r2), max(r1, r2)
    fc1, fc2 = min(c1, c2), max(c1, c2)
    
    # 2. 유효 범위인지 확인
    if 0 <= fr1 < NUM_ROWS and 0 <= fc1 < NUM_COLS:
        # 3. 서버로 MOVE 명령 전송
        if CLIENT_SOCKET:
            msg = f"MOVE {fr1} {fc1} {fr2} {fc2}"
            try:
                CLIENT_SOCKET.send(msg.encode('utf-8'))
                print(f"[서버로 전송]: {msg}")
            except:
                print("전송 실패")
        else:
            print("서버 연결이 필요합니다.")

    clear_selection_rectangle()
    start_x, start_y = -1, -1

def handle_pass():
    # 스킵 기능 (구현 필요 시 서버로 PASS 전송)
    pass

def initialize_game(first_player_is_human=True):
    global current_game
    # 임시 보드 생성 (나중에는 서버에서 받아와야 함)
    new_board = []
    for r in range(NUM_ROWS):
        row = []
        for c in range(NUM_COLS):
            row.append(random.randint(1, 9))
        new_board.append(row)
        
    current_game = Game(new_board, first_player_is_human)
    draw_board()
    update_canvas_cursor()

# ================================
# 메인 실행
# ================================
if __name__ == "__main__":
    canvas.bind("<ButtonPress-1>", on_canvas_press)
    canvas.bind("<B1-Motion>", on_canvas_drag)
    canvas.bind("<ButtonRelease-1>", on_canvas_release)
    canvas.bind("<Enter>", lambda event: update_canvas_cursor())
    
    initialize_game()
    
    root.mainloop()