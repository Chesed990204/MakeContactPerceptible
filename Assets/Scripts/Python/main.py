# import socket
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import time
# import pandas as pd
# import datetime
# import math

# # 데이터 리스트
# time_data = []
# palm_x, palm_y, palm_z = [], [], []
# index_x, index_y, index_z = [], [], []
# palm_v, palm_a = [], []
# index_v, index_a = [], []
# states = []

# start_time = time.time()

# # 색상 정의
# state_colors = {
#     "Start": "blue",
#     "Approach": "green",
#     "Click": "red",
#     "Overshoot": "orange",
#     "Withdraw": "purple",
#     "End": "black",
#     "None": "gray"
# }

# # Figure
# fig, axs = plt.subplots(4, 3, figsize=(12, 10))
# titles = [
#     "Palm X", "Palm Y", "Palm Z",
#     "Index X", "Index Y", "Index Z",
#     "Palm Velocity Magnitude", "Index Velocity Magnitude",
#     "Palm Acceleration Magnitude", "Index Acceleration Magnitude"
# ]

# # 속도 magnitude 계산 함수
# def compute_velocity_magnitude(x_list, y_list, z_list, time_list):
#     if len(time_list) < 2:
#         return 0.0
#     dx = x_list[-1] - x_list[-2]
#     dy = y_list[-1] - y_list[-2]
#     dz = z_list[-1] - z_list[-2]
#     dt = time_list[-1] - time_list[-2]
#     if dt <= 0:
#         return 0.0
#     return math.sqrt(dx**2 + dy**2 + dz**2) / dt

# # 가속도 magnitude 계산 함수
# def compute_acceleration_magnitude(v_list, time_list):
#     if len(v_list) < 2:
#         return 0.0
#     dv = v_list[-1] - v_list[-2]
#     dt = time_list[-1] - time_list[-2]
#     if dt <= 0:
#         return 0.0
#     return abs(dv) / dt

# # 데이터 파싱 함수
# def parse_data(msg):
#     vec1_str, vec2_str, state = msg.strip().split('|')
#     palm_x_val, palm_y_val, palm_z_val = map(float, vec1_str.split(','))
#     index_x_val, index_y_val, index_z_val = map(float, vec2_str.split(','))
#     state = state.strip()
#     return palm_x_val, palm_y_val, palm_z_val, index_x_val, index_y_val, index_z_val, state

# # CSV 저장 함수
# def get_datetime_filename(prefix="hand_motion_log"):
#     now = datetime.datetime.now()
#     filename = f"Python/hand_data/{prefix}_{now.strftime('%Y%m%d_%H%M%S')}.csv"
#     return filename

# def save_trial(trial_data):
#     df = pd.DataFrame(trial_data)
#     filename = get_datetime_filename(prefix="trial")
#     df.to_csv(filename, index=False)
#     print(f"[INFO] Trial saved to {filename}")

# # 실시간 플롯 업데이트 함수
# def update_plot(frame):
#     y_lists = [
#         palm_x, palm_y, palm_z,
#         index_x, index_y, index_z,
#         palm_v, index_v,
#         palm_a, index_a
#     ]

#     for i, y_data in enumerate(y_lists):
#         row, col = divmod(i, 3)
#         axs[row][col].cla()
#         axs[row][col].set_title(titles[i])
#         axs[row][col].set_xlabel("Time (s)")
#         axs[row][col].set_ylabel("Value")

#         for t, y, state in zip(time_data, y_data, states):
#             color = state_colors.get(state.strip(), 'gray')
#             axs[row][col].plot(t, y, 'o', color=color, markersize=3)

#     handles = [plt.Line2D([0], [0], marker='o', color='w',
#                           markerfacecolor=c, markersize=8, label=s)
#                for s, c in state_colors.items()]
#     fig.legend(handles=handles, loc='upper center', ncol=7, fontsize=8, bbox_to_anchor=(0.5, 0.98))
#     plt.subplots_adjust(
#     top=0.92, 
#     right=0.95, 
#     wspace=0.3,  # 가로 간격
#     hspace=0.5   # 세로 간격
# )
#     return []

# # 서버 함수
# def start_server():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind(('127.0.0.1', 25001))
#         s.listen(1)
#         print("Listening for connection...")
#         conn, addr = s.accept()
#         print(f"Connected by {addr}")

#         with conn:
#             while True:
#                 data = conn.recv(1024)
#                 if not data:
#                     break
#                 try:
#                     parsed = parse_data(data.decode('utf-8'))
#                     palm_x_val, palm_y_val, palm_z_val, index_x_val, index_y_val, index_z_val, state = parsed
#                     t = time.time() - start_time

#                     time_data.append(t)
#                     palm_x.append(palm_x_val)
#                     palm_y.append(palm_y_val)
#                     palm_z.append(palm_z_val)
#                     index_x.append(index_x_val)
#                     index_y.append(index_y_val)
#                     index_z.append(index_z_val)
#                     states.append(state)

#                     # 속도 magnitude
#                     palm_velocity = compute_velocity_magnitude(palm_x, palm_y, palm_z, time_data)
#                     index_velocity = compute_velocity_magnitude(index_x, index_y, index_z, time_data)
#                     palm_v.append(palm_velocity)
#                     index_v.append(index_velocity)

#                     # 가속도 magnitude
#                     palm_acceleration = compute_acceleration_magnitude(palm_v, time_data)
#                     index_acceleration = compute_acceleration_magnitude(index_v, time_data)
#                     palm_a.append(palm_acceleration)
#                     index_a.append(index_acceleration)

#                     if state == "Start":
#                         current_trial = []  # 새 trial 시작

#                     current_trial.append({
#                         'time': t,
#                         'palm_x': palm_x_val,
#                         'palm_y': palm_y_val,
#                         'palm_z': palm_z_val,
#                         'index_x': index_x_val,
#                         'index_y': index_y_val,
#                         'index_z': index_z_val,
#                         'palm_v': palm_velocity,
#                         'palm_a': palm_acceleration,
#                         'index_v': index_velocity,
#                         'index_a': index_acceleration,
#                         'state': state
#                     })

#                     if state == "End" and current_trial:
#                         save_trial(current_trial)
#                         current_trial = []

#                     conn.sendall(b"OK")

#                 except Exception as e:
#                     print("Parse error:", e)

# # 실행
# import threading
# threading.Thread(target=start_server, daemon=True).start()

# ani = FuncAnimation(fig, update_plot, interval=500)
# plt.show()

import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import pandas as pd
import datetime
import ast

# 데이터 저장용
trial_indexZ = []
trial_metadata = {}

fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot([], [], 'o-', label='Index Z')
maxZ_marker = ax.axhline(0, color='red', linestyle='--', label='Max Z')
impact_marker = ax.axhline(0, color='green', linestyle='--', label='Impact Point')
text_box = ax.text(0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top')

def parse_data(msg):
    # trial:1|indexZs:[0.1,0.2]|maxZ:0.3|impact:0.1|error:0.2
    items = msg.strip().split('|')
    data = {}
    for item in items:
        key, val = item.split(':', 1)
        if key == "indexZs":
            data[key] = ast.literal_eval(val)  # safely convert '[...]' to list
        else:
            data[key] = float(val)
    return data

def save_trial(indexZ_list, metadata):
    df = pd.DataFrame({'index_z': indexZ_list})
    for key in ['trial', 'maxZ', 'impact', 'error']:
        df[key] = metadata[key]
    filename = f'Python/hand_data/trial_{int(metadata["trial"]):03d}_{datetime.datetime.now().strftime("%H%M%S")}.csv'
    df.to_csv(filename, index=False)
    print(f"[Saved] {filename}")

def update_plot(frame):
    if not trial_indexZ:
        return []
    x = list(range(len(trial_indexZ)))
    y = trial_indexZ
    line.set_data(x, y)
    ax.set_xlim(0, max(10, len(x)))
    ax.set_ylim(min(y) - 0.01, max(y) + 0.01)
    maxZ_marker.set_ydata([trial_metadata['maxZ']])
    impact_marker.set_ydata([trial_metadata['impact']])

    text_box.set_text(f"Trial {int(trial_metadata['trial'])}\nError: {trial_metadata['error']:.5f}")
    return [line, maxZ_marker, impact_marker, text_box]

def start_server():
    global trial_indexZ, trial_metadata
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 25001))
        s.listen(1)
        print("Listening for connection...")
        conn, addr = s.accept()
        print(f"Connected by {addr}")

        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                try:
                    decoded = data.decode('utf-8')
                    parsed = parse_data(decoded)
                    trial_indexZ = parsed['indexZs']
                    trial_metadata = parsed
                    save_trial(trial_indexZ, trial_metadata)
                    conn.sendall(b"OK")
                except Exception as e:
                    print("Parse error:", e)

import threading
threading.Thread(target=start_server, daemon=True).start()

ani = FuncAnimation(fig, update_plot, interval=1000)
plt.legend()
plt.tight_layout()
plt.show()
