import tkinter as tk
import math
import random
import winsound

# iestatījumi
SOFT_BOILED_SECONDS = 4 * 60
MEDIUM_BOILED_SECONDS   = 7 * 60
HARD_BOILED_SECONDS= 12 * 60

COLOR_BG = "#F9E4CD"
COLOR_CARD   = "#DEDEDD"
COLOR_SOFT = "#E8860D"
COLOR_MEDIUM     = "#EDA23A"
COLOR_HARD = "#EFE166"
COLOR_TEXT = "#000000"
COLOR_DIM  = "#B8A9A0"
COLOR_DONE = "#A7E8BD"
COLOR_PONG_BG= "#FFFFFF"

FONT_TITLE = ("Helvetica", 20, "bold")
FONT_MAIN = ("Helvetica", 12)
FONT_TIMER= ("Helvetica", 32, "bold")


def play_beep():
  winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

# pong spēle

PONG_WIDTH = 360
PONG_HEIGHT = 220
PADDLE_W = 8
PADDLE_H  = 40
BALL_RADIUS = 6
BALL_SPEED = 4.5

pong_running = False
pong_job = None

ball_x = PONG_WIDTH / 2
ball_y = PONG_HEIGHT / 2
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED

left_paddle_y = PONG_HEIGHT // 2 - PADDLE_H // 2
right_paddle_y  = PONG_HEIGHT // 2 - PADDLE_H // 2

score = [0, 0]
keys = {"w": False, "s": False}


def on_key_press(event):
    if event.keysym.lower() == "w":
        keys["w"] = True
    elif event.keysym.lower() == "s":
      keys["s"] = True


def on_key_release(event):
    if event.keysym.lower() == "w": keys["w"] = False
    elif event.keysym.lower() == "s":
        keys["s"] = False


def pong_start():
    global pong_running, ball_x, ball_y, ball_dx, ball_dy, score
    if pong_running:
        return
    pong_running = True
    score = [0, 0]
    ball_x = PONG_WIDTH / 2
    ball_y = PONG_HEIGHT / 2
    angle = random.uniform(-0.5, 0.5)
    direction = random.choice([-1, 1])
    ball_dx = BALL_SPEED * direction
    ball_dy  = BALL_SPEED * math.sin(angle)
    pong_loop()

def pong_stop():
    global pong_running, pong_job
    pong_running = False
    if pong_job: canvas.after_cancel(pong_job)
    pong_job = None



def pong_move():
    global left_paddle_y, right_paddle_y
    speed = 6
    if keys["w"]:
        left_paddle_y = max(0, left_paddle_y - speed)
    if keys["s"]:
      left_paddle_y = min(PONG_HEIGHT - PADDLE_H, left_paddle_y + speed)
    # AI
    ai_speed = 4
    center = right_paddle_y + PADDLE_H / 2
    if center < ball_y:
        right_paddle_y += ai_speed
    elif center > ball_y:
        right_paddle_y -= ai_speed


def pong_loop():
    global ball_x, ball_y, ball_dx, ball_dy, score, pong_job

    if not pong_running:
        return

    pong_move()
    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= PONG_HEIGHT: ball_dy *= -1

    if ball_x <= 10 and left_paddle_y <= ball_y <= left_paddle_y + PADDLE_H:
        ball_dx = abs(ball_dx)
    if ball_x >= PONG_WIDTH - 10 and right_paddle_y <= ball_y <= right_paddle_y + PADDLE_H:
        ball_dx = -abs(ball_dx)

    if ball_x < 0:
      score[1] += 1
      reset_ball()
    if ball_x > PONG_WIDTH:
        score[0] += 1
        reset_ball()

    draw_pong()
    pong_job = canvas.after(16, pong_loop)


def reset_ball():
  global ball_x, ball_y, ball_dx
  ball_x, ball_y = PONG_WIDTH/2, PONG_HEIGHT/2
  ball_dx *= -1


def draw_pong():
    canvas.delete("all")
    canvas.create_rectangle(1, 1, PONG_WIDTH, PONG_HEIGHT, fill=COLOR_PONG_BG, outline="")
    canvas.create_rectangle(
        5, left_paddle_y, 5+PADDLE_W, left_paddle_y+PADDLE_H, fill="#00AEFF")
    canvas.create_rectangle(PONG_WIDTH-5-PADDLE_W, right_paddle_y,
                            PONG_WIDTH-5, right_paddle_y+PADDLE_H, fill="#FF3300")
    canvas.create_oval(ball_x-6, ball_y-6, ball_x+6, ball_y+6, fill="#FFFFFF")
    canvas.create_text(PONG_WIDTH/2-20, 10, text=score[0], fill=COLOR_DIM)
    canvas.create_text(PONG_WIDTH/2+20, 10, text=score[1], fill=COLOR_DIM)

## taimeris

timers = {
    "mīksts":   {"name": "Mīksti", "time": SOFT_BOILED_SECONDS,   "color": COLOR_SOFT},
    "vidējs": {"name": "Vidēji","time": MEDIUM_BOILED_SECONDS, "color": COLOR_MEDIUM},
    "ciets":   {"name": "Cieti",  "time": HARD_BOILED_SECONDS, "color": COLOR_HARD},
}


def start_timer(seconds):
    global remaining
    pong_stop()
    remaining = seconds
    update_timer()
    pong_start()

def update_timer():
    global remaining
    if remaining <= 0:
        label.config(text="GATAVS!")
        play_beep()
        pong_stop()
        return
    mins = remaining // 60
    secs = remaining % 60
    label.config(text=f"{mins:02}:{secs:02}")
    remaining -= 1
    window.after(1000, update_timer)

# UI --------------------------------------------------

window = tk.Tk()
window.title("Olu taimeris")
window.configure(bg=COLOR_BG)
window.bind("<KeyPress>",   on_key_press)
window.bind("<KeyRelease>", on_key_release)
window.focus_set()

tk.Label(window, text="Olu taimeris",
         font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=10)

label = tk.Label(window, text="00:00", font=FONT_TIMER, bg=COLOR_BG, fg=COLOR_TEXT)
label.pack()

frame = tk.Frame(window, bg=COLOR_BG)
frame.pack(pady=10)

for key in timers:
  t = timers[key]
  tk.Button(frame,
            text=t["name"],
            bg=t["color"], fg=COLOR_TEXT,
            font=FONT_MAIN, width=10,
            command=lambda s=t["time"]: start_timer(s)
            ).pack(side="left", padx=5)

canvas = tk.Canvas(window, width=PONG_WIDTH, height=PONG_HEIGHT,
                   bg=COLOR_PONG_BG, highlightthickness=0)
canvas.pack(pady=10)

tk.Label(window, text="Zilais taisnstūris, W un S lai kustētos",
         font=("Helvetica", 9), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=5)

window.mainloop()