# import matplotlib.pyplot as plt
# import pandas as pd
# import os
# import glob

# # 🔹 1) 데이터 파일 목록 읽기
# trial_files = sorted(glob.glob("hand_data/trial_*.csv"))


# if not trial_files:
#     print("No trial files found.")
#     exit()

# # 🔹 2) State별 색상
# state_colors = {
#     "Start": "blue",
#     "Approach": "green",
#     "Click": "red",
#     "Overshoot": "orange",
#     "Withdraw": "purple",
#     "End": "black",
#     "None": "gray"
# }

# # 🔹 3) Trial index
# current_trial_index = 0

# # 🔹 4) Figure 초기화
# fig, axs = plt.subplots(4, 3, figsize=(12, 10))
# titles = [
#     "Palm X", "Palm Y", "Palm Z",
#     "Index X", "Index Y", "Index Z",
#     "Palm Velocity Magnitude", "Index Velocity Magnitude",
#     "Palm Acceleration Magnitude", "Index Acceleration Magnitude"
# ]

# # 🔹 5) Plot 함수
# def plot_trial(index):
#     for ax in axs.flat:
#         ax.clear()
#     if index >= len(trial_files):
#         print("No more trials.")
#         return
#     filename = trial_files[index]
#     df = pd.read_csv(filename)
#     time_data = df['time']

#     # 🔹 y_lists 확장
#     y_lists = [
#         df['palm_x'], df['palm_y'], df['palm_z'],
#         df['index_x'], df['index_y'], df['index_z'],
#         df['palm_v'], df['index_v'],
#         df['palm_a'], df['index_a']
#     ]

#     states = df['state']

#     for i, y_data in enumerate(y_lists):
#         row, col = divmod(i, 3)
#         axs[row][col].set_title(titles[i])
#         axs[row][col].set_xlabel("Time (s)")
#         axs[row][col].set_ylabel("Value")

#         for t, y, state in zip(time_data, y_data, states):
#             state_str = str(state).strip()
#             color = state_colors.get(state_str, 'gray')
#             axs[row][col].plot(t, y, 'o', color=color, markersize=3)

#     # 🔹 Figure-level Legend
#     handles = [plt.Line2D([0], [0], marker='o', color='w', 
#                           markerfacecolor=c, markersize=8, label=s)
#                for s, c in state_colors.items()]
#     fig.legend(handles=handles, loc='upper center', ncol=7, fontsize=8, bbox_to_anchor=(0.5, 0.97))

#     fig.suptitle(f"Trial: {os.path.basename(filename)} ({index+1}/{len(trial_files)})")
#     plt.subplots_adjust(top=0.92, right=0.95, wspace=0.3, hspace=0.4)
#     plt.draw()

# # 🔹 6) 초기 plot
# plot_trial(current_trial_index)

# # 🔹 7) 키 입력 핸들러
# def on_key(event):
#     global current_trial_index, trial_files
#     if event.key == 'right':
#         current_trial_index += 1
#         if current_trial_index >= len(trial_files):
#             current_trial_index = 0  # loop around
#         plot_trial(current_trial_index)

#     elif event.key == 'left':
#         current_trial_index -= 1
#         if current_trial_index < 0:
#             current_trial_index = len(trial_files) - 1
#         plot_trial(current_trial_index)

#     elif event.key == 'd':
#         filename = trial_files[current_trial_index]
#         confirm = input(f"Delete {filename}? (y/n): ").strip().lower()
#         if confirm == 'y':
#             os.remove(filename)
#             print(f"[Deleted] {filename}")
#             # Remove from list
#             del trial_files[current_trial_index]
#             if len(trial_files) == 0:
#                 print("No more trials.")
#                 plt.close(fig)
#                 return
#             current_trial_index %= len(trial_files)
#             plot_trial(current_trial_index)

# fig.canvas.mpl_connect('key_press_event', on_key)

# plt.show()


import matplotlib.pyplot as plt
import pandas as pd
import os
import glob

trial_files = sorted(glob.glob("Python/hand_data/trial_*.csv"))
if not trial_files:
    print("No trial files found.")
    exit()

fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot([], [], 'o-', label='Index Z')
maxZ_marker = ax.axhline(0, color='red', linestyle='--', label='Max Z')
impact_marker = ax.axhline(0, color='green', linestyle='--', label='Impact Point')
text_box = ax.text(0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top')

current_trial_index = 0

def plot_trial(index):
    if index >= len(trial_files): return
    df = pd.read_csv(trial_files[index])
    y = df['index_z'].tolist()
    x = list(range(len(y)))
    trial = df['trial'].iloc[0]
    maxZ = df['maxZ'].iloc[0]
    impact = df['impact'].iloc[0]
    error = df['error'].iloc[0]

    ax.clear()
    ax.plot(x, y, 'o-', label='Index Z')
    ax.axhline(maxZ, color='red', linestyle='--', label='Max Z')
    ax.axhline(impact, color='green', linestyle='--', label='Impact')
    ax.set_title(f"Trial {int(trial)} - Error: {error:.5f}")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Index Z")
    ax.legend()
    plt.draw()

plot_trial(current_trial_index)

def on_key(event):
    global current_trial_index
    if event.key == 'right':
        current_trial_index = (current_trial_index + 1) % len(trial_files)
        plot_trial(current_trial_index)
    elif event.key == 'left':
        current_trial_index = (current_trial_index - 1) % len(trial_files)
        plot_trial(current_trial_index)
    elif event.key == 'd':
        f = trial_files[current_trial_index]
        confirm = input(f"Delete {f}? (y/n): ").strip().lower()
        if confirm == 'y':
            os.remove(f)
            trial_files.pop(current_trial_index)
            current_trial_index %= len(trial_files)
            plot_trial(current_trial_index)

fig.canvas.mpl_connect('key_press_event', on_key)
plt.tight_layout()
plt.show()
