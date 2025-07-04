# import matplotlib.pyplot as plt
# import pandas as pd
# import os
# import glob

# trial_files = sorted(glob.glob("episode_data/예서_Visual/trials/trial_*.csv"))
# if not trial_files:
#     print("No trial files found.")
#     exit()

# fig, ax = plt.subplots(figsize=(10, 5))
# line, = ax.plot([], [], 'o-', label='Index Z')
# maxZ_marker = ax.axhline(0, color='red', linestyle='--', label='Max Z')
# impact_marker = ax.axhline(0, color='green', linestyle='--', label='Impact Point')
# text_box = ax.text(0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top')

# current_trial_index = 0

# def plot_trial(index):
#     if index >= len(trial_files): return
#     df = pd.read_csv(trial_files[index])
#     y = df['index_z'].tolist()
#     x = list(range(len(y)))
#     trial = df['trial'].iloc[0]
#     maxZ = df['maxZ'].iloc[0]
#     impact = df['impact'].iloc[0]
#     error = df['error'].iloc[0]

#     ax.clear()
#     ax.plot(x, y, 'o-', label='Index Z')
#     ax.axhline(maxZ, color='red', linestyle='--', label='Max Z')
#     ax.axhline(impact, color='green', linestyle='--', label='Impact')
#     ax.set_title(f"Trial {int(trial)} - Error: {error:.5f}")
#     ax.set_xlabel("Frame")
#     ax.set_ylabel("Index Z")
#     ax.legend()
#     plt.draw()

# plot_trial(current_trial_index)

# def on_key(event):
#     global current_trial_index
#     if event.key == 'right':
#         current_trial_index = (current_trial_index + 1) % len(trial_files)
#         plot_trial(current_trial_index)
#     elif event.key == 'left':
#         current_trial_index = (current_trial_index - 1) % len(trial_files)
#         plot_trial(current_trial_index)
#     elif event.key == 'd':
#         f = trial_files[current_trial_index]
#         confirm = input(f"Delete {f}? (y/n): ").strip().lower()
#         if confirm == 'y':
#             os.remove(f)
#             trial_files.pop(current_trial_index)
#             current_trial_index %= len(trial_files)
#             plot_trial(current_trial_index)

# fig.canvas.mpl_connect('key_press_event', on_key)
# plt.tight_layout()
# plt.show()

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import os
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import sys # sys.exit()를 위해
import glob # 파일 패턴 매칭을 위해

# --- Configuration (main.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # main.py와 동일하게 설정

# --- Global Variables for Viewer ---
all_loaded_trials = [] # 모든 로드된 trial 데이터를 저장할 리스트 (indexZ_list, metadata)
all_loaded_episodes = [] # 모든 로드된 episode 데이터를 저장할 리스트 (dict)
current_trial_idx = -1 # 현재 표시 중인 trial의 인덱스
selected_user_folder = "" # 선택된 사용자 폴더 경로
selected_feedback_type_subdir = "" # 선택된 피드백 타입 서브 폴더 (예: "0.Visual")
selected_feedback_type_name = "" # 선택된 피드백 타입의 이름 (예: "OnlyVisual")


# --- Matplotlib Plot Setup (main.py와 유사) ---
fig, axs = plt.subplots(2, 3, figsize=(20, 10))
fig.suptitle('Button Press Experiment Data Viewer', fontsize=16)


# axs[0,0]: 개별 Trial의 Index Z 변화 (현재 Trial)
ax1 = axs[0, 0]
line, = ax1.plot([], [], 'o-', label='Index Z')
maxZ_marker = ax1.axhline(0, color='red', linestyle='--', label='Max Z')
impact_marker = ax1.axhline(0, color='green', linestyle='--', label='Impact Point')
trial_info_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, verticalalignment='top')
ax1.legend()
ax1.set_title('Index Z per Trial (Current)')
ax1.set_xlabel("Time Step")
ax1.set_ylabel("Index Z Position (m)")
ax1.grid(True)


# axs[0,1]: Episode별 MaxZ 평균 및 분산
ax2 = axs[0, 1]
episode_means_line, = ax2.plot([], [], 'b-o', label='Mean MaxZ')
episode_stds_line, = ax2.plot([], [], 'r--x', label='Std Dev MaxZ')
episode_maxz_text_box = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, verticalalignment='top')
ax2.legend()
ax2.set_title(f'Episode Statistics: MaxZ (Trials per Episode: {TRIALS_PER_EPISODE})')
ax2.set_xlabel("Episode Number")
ax2.set_ylabel("Max Z Value (m)")
ax2.grid(True)


# axs[1,0]: Episode별 Error 평균 및 분산
ax3 = axs[1, 0]
episode_error_means_line, = ax3.plot([], [], 'g-o', label='Mean Error')
episode_error_stds_line, = ax3.plot([], [], 'm--x', label='Std Dev Error')
episode_error_text_box = ax3.text(0.02, 0.95, '', transform=ax3.transAxes, verticalalignment='top')
ax3.legend()
ax3.set_title(f'Episode Statistics: Error (Trials per Episode: {TRIALS_PER_EPISODE})')
ax3.set_xlabel("Episode Number")
ax3.set_ylabel("Error (m)")
ax3.grid(True)


# axs[1,1]: 이전 Trial의 Index Z 변화
ax4 = axs[1, 1]
line_prev, = ax4.plot([], [], 'o-', color='purple', label='Prev Index Z')
maxZ_marker_prev = ax4.axhline(0, color='orange', linestyle='--', label='Prev Max Z')
impact_marker_prev = ax4.axhline(0, color='cyan', linestyle='--', label='Prev Impact Point')
trial_info_text_prev = ax4.text(0.02, 0.95, '', transform=ax4.transAxes, verticalalignment='top')
ax4.legend()
ax4.set_title('Index Z per Trial (Previous)')
ax4.set_xlabel("Time Step")
ax4.set_ylabel("Index Z Position (m)")
ax4.grid(True)


# axs[0,2]: Episode별 Impact Position 평균 및 분산
ax5 = axs[0, 2]
episode_impact_means_line, = ax5.plot([], [], 'c-o', label='Mean Impact Pos')
episode_impact_stds_line, = ax5.plot([], [], 'y--x', label='Std Dev Impact Pos')
episode_impact_text_box = ax5.text(0.02, 0.95, '', transform=ax5.transAxes, verticalalignment='top')
ax5.legend()
ax5.set_title(f'Episode Statistics: Impact Position (Trials per Episode: {TRIALS_PER_EPISODE})')
ax5.set_xlabel("Episode Number")
ax5.set_ylabel("Impact Position (m)")
ax5.grid(True)


def load_data_for_feedback_type(user_folder_path, feedback_type_key, subdir_name):
    """
    지정된 사용자 폴더와 피드백 타입에 해당하는 trial 및 episode 데이터를 로드합니다.
    """
    global all_loaded_trials, all_loaded_episodes

    # 이 함수는 특정 피드백 타입에 대한 데이터만 로드하므로,
    # 전역 리스트를 여기에 초기화하면 안 됩니다.
    # start_viewer에서 초기화하거나, append 시 중복 체크해야 합니다.
    # 여기서는 호출 전에 초기화되어 있다고 가정하고 append만 수행합니다.

    trials_dir = os.path.join(user_folder_path, subdir_name, "trials")
    episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")

    print(f"  Loading data from: {feedback_type_key} ({trials_dir})")

    # Load trials data
    if os.path.exists(trials_dir):
        trial_files = sorted(glob.glob(os.path.join(trials_dir, 'trial_*.csv')))
        for t_file_path in trial_files:
            try:
                df_trial = pd.read_csv(t_file_path)
                if not df_trial.empty:
                    last_row = df_trial.iloc[-1]
                    
                    indexZs_list = df_trial['index_z'].astype(float).tolist()

                    metadata = {
                        'trial': float(last_row['trial']),
                        'maxZ': float(last_row['maxZ']),
                        'impact': float(last_row['impact']),
                        'error': float(last_row['error']),
                        'feedbackType': last_row['feedbackType']
                    }
                    all_loaded_trials.append((indexZs_list, metadata))
                    
            except Exception as e:
                print(f"Error loading trial file {t_file_path}: {e}")

    # Load episode data
    if os.path.exists(episode_stats_dir):
        episode_files = sorted(glob.glob(os.path.join(episode_stats_dir, 'episode_data_ep*.csv')))
        for e_file_path in episode_files:
            try:
                df_episode = pd.read_csv(e_file_path)
                if not df_episode.empty:
                    episode_entry = df_episode.iloc[0].to_dict()
                    
                    if 'all_maxZs_in_episode' in episode_entry and isinstance(episode_entry['all_maxZs_in_episode'], str):
                        parsed_list = ast.literal_eval(episode_entry['all_maxZs_in_episode'])
                        episode_entry['all_maxZs_in_episode'] = list(map(float, parsed_list))
                    else:
                        episode_entry['all_maxZs_in_episode'] = []

                    if 'all_errors_in_episode' in episode_entry and isinstance(episode_entry['all_errors_in_episode'], str):
                        parsed_list = ast.literal_eval(episode_entry['all_errors_in_episode'])
                        episode_entry['all_errors_in_episode'] = list(map(float, parsed_list))
                    else:
                        episode_entry['all_errors_in_episode'] = []

                    if 'all_impacts_in_episode' in episode_entry and isinstance(episode_entry['all_impacts_in_episode'], str):
                        parsed_list = ast.literal_eval(episode_entry['all_impacts_in_episode'])
                        episode_entry['all_impacts_in_episode'] = list(map(float, parsed_list))
                    else:
                        episode_entry['all_impacts_in_episode'] = []

                    if 'mean_maxZ' in episode_entry: episode_entry['mean_maxZ'] = float(episode_entry['mean_maxZ'])
                    if 'std_maxZ' in episode_entry: episode_entry['std_maxZ'] = float(episode_entry['std_maxZ'])
                    if 'mean_error' in episode_entry: episode_entry['mean_error'] = float(episode_entry['mean_error'])
                    if 'std_error' in episode_entry: episode_entry['std_error'] = float(episode_entry['std_error'])
                    if 'mean_impact' in episode_entry: episode_entry['mean_impact'] = float(episode_entry['mean_impact'])
                    if 'std_impact' in episode_entry: episode_entry['std_impact'] = float(episode_entry['std_impact'])
                    if 'episode_num' in episode_entry: episode_entry['episode_num'] = int(episode_entry['episode_num'])
                    if 'feedback_type' not in episode_entry: episode_entry['feedback_type'] = feedback_type_key

                    all_loaded_episodes.append(episode_entry)

            except Exception as e:
                print(f"Error loading episode file {e_file_path}: {e}")

    # episode_data는 episode_num 기준으로 정렬되어야 합니다.
    # all_loaded_episodes는 이제 단일 피드백 타입에 대한 것이므로, 
    # 이후에 전체 에피소드를 다룰 때 다시 정렬해야 합니다.
    # 여기서는 현재 로드된 에피소드만 정렬
    all_loaded_episodes.sort(key=lambda x: x['episode_num'])


def update_plot_with_current_trial():
    """
    현재 trial_idx에 해당하는 데이터를 가져와 플롯을 업데이트합니다.
    """
    global current_trial_idx, all_loaded_trials, all_loaded_episodes, selected_feedback_type_name

    if not all_loaded_trials:
        # 모든 플롯 초기화 (로드된 트라이얼이 없거나 선택된 타입에 트라이얼이 없을 경우)
        line.set_data([], [])
        maxZ_marker.set_ydata([0])
        impact_marker.set_ydata([0])
        trial_info_text.set_text("No trial data loaded for this type.")
        
        episode_means_line.set_data([], [])
        episode_stds_line.set_data([], [])
        episode_maxz_text_box.set_text("No episode data loaded for this type.")
        
        episode_error_means_line.set_data([], [])
        episode_error_stds_line.set_data([], [])
        episode_error_text_box.set_text("No episode data loaded for this type.")

        line_prev.set_data([], [])
        maxZ_marker_prev.set_ydata([0])
        impact_marker_prev.set_ydata([0])
        trial_info_text_prev.set_text("No previous trial data for this type.")

        episode_impact_means_line.set_data([], [])
        episode_impact_stds_line.set_data([], [])
        episode_impact_text_box.set_text("No episode data loaded for this type.")
        
        fig.canvas.draw_idle()
        return


    # 현재 트라이얼 데이터
    current_trial_data = all_loaded_trials[current_trial_idx]
    current_indexZ, current_metadata = current_trial_data

    # 이전 트라이얼 데이터 (있다면)
    prev_indexZ_data = []
    prev_metadata_data = {}
    if current_trial_idx > 0:
        prev_trial_data = all_loaded_trials[current_trial_idx - 1]
        prev_indexZ_data, prev_metadata_data = prev_trial_data

    # 현재 트라이얼 플롯 업데이트
    x = list(range(len(current_indexZ)))
    y = current_indexZ
    line.set_data(x, y)
    ax1.set_xlim(0, max(10, len(x)))
    ax1.set_ylim(min(y) - 0.01, max(y) + 0.01)
    maxZ_marker.set_ydata([current_metadata['maxZ']])
    impact_marker.set_ydata([current_metadata['impact']])
    
    # 에피소드 진행 상황 추정 (선택된 피드백 타입 내에서)
    # 현재 트라이얼의 trial 번호를 사용하여 해당 피드백 타입 내에서의 상대적 에피소드 번호 추정
    # all_loaded_trials는 이제 이미 필터링된 리스트이므로 current_trial_idx 자체가 해당 피드백 타입 내 인덱스
    episode_progress_count = (current_trial_idx % TRIALS_PER_EPISODE) + 1
    episode_num_in_type = current_trial_idx // TRIALS_PER_EPISODE + 1

    trial_info_text.set_text(f"Trial {int(current_metadata['trial'])} (Viewer Index: {current_trial_idx+1}/{len(all_loaded_trials)})\n"
                             f"Type: {current_metadata['feedbackType']}\n"
                             f"Error: {current_metadata['error']:.5f}\n"
                             f"Episode Progress (Type): {episode_progress_count}/{TRIALS_PER_EPISODE} (Ep {episode_num_in_type})")


    # 이전 트라이얼 플롯 업데이트
    if prev_indexZ_data and prev_metadata_data:
        x_prev = list(range(len(prev_indexZ_data)))
        y_prev = prev_indexZ_data
        line_prev.set_data(x_prev, y_prev)
        ax4.set_xlim(0, max(10, len(x_prev)))
        ax4.set_ylim(min(y_prev) - 0.01, max(y_prev) + 0.01)
        maxZ_marker_prev.set_ydata([prev_metadata_data['maxZ']])
        impact_marker_prev.set_ydata([prev_metadata_data['impact']])
        trial_info_text_prev.set_text(f"Prev Trial {int(prev_metadata_data['trial'])}\n"
                                      f"Type: {prev_metadata_data.get('feedbackType', 'UNKNOWN')}\nError: {prev_metadata_data['error']:.5f}")
    else:
        line_prev.set_data([], [])
        maxZ_marker_prev.set_ydata([0])
        impact_marker_prev.set_ydata([0])
        trial_info_text_prev.set_text("No previous trial data")
        ax4.set_xlim(0, 10)
        ax4.set_ylim(-0.1, 0.3)


    # 에피소드 통계 플롯 업데이트 (현재 선택된 피드백 타입의 에피소드 데이터만 사용)
    if all_loaded_episodes: # all_loaded_episodes는 이제 이미 필터링된 리스트
        episode_numbers = [d['episode_num'] for d in all_loaded_episodes]
        
        episode_means = [d['mean_maxZ'] for d in all_loaded_episodes]
        episode_stds = [d['std_maxZ'] for d in all_loaded_episodes]
        episode_means_line.set_data(episode_numbers, episode_means)
        episode_stds_line.set_data(episode_numbers, episode_stds)
        
        all_max_z_values_ep = [m for d in all_loaded_episodes for m in d.get('all_maxZs_in_episode', [])]
        if all_max_z_values_ep:
            min_y2 = min(all_max_z_values_ep) - 0.02
            max_y2 = max(all_max_z_values_ep) + 0.02
            if abs(max_y2 - min_y2) < 0.01:
                center = (min_y2 + max_y2) / 2
                min_y2 = center - 0.005
                max_y2 = center + 0.005
            ax2.set_ylim(min_y2, max_y2)
        else:
            ax2.set_ylim(0, 0.3)
        ax2.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        latest_episode_num = all_loaded_episodes[-1]['episode_num']
        latest_maxz_mean = all_loaded_episodes[-1]['mean_maxZ']
        latest_maxz_std = all_loaded_episodes[-1]['std_maxZ']
        episode_maxz_text_box.set_text(f"Ep {latest_episode_num} ({selected_feedback_type_name})\nMean: {latest_maxz_mean:.5f}\nStd Dev: {latest_maxz_std:.5f}")


        episode_error_means = [d['mean_error'] for d in all_loaded_episodes]
        episode_error_stds = [d['std_error'] for d in all_loaded_episodes]
        episode_error_means_line.set_data(episode_numbers, episode_error_means)
        episode_error_stds_line.set_data(episode_numbers, episode_error_stds)
        
        all_error_values_ep = [e for d in all_loaded_episodes for e in d.get('all_errors_in_episode', [])]
        if all_error_values_ep:
            min_y3 = min(all_error_values_ep) - 0.02
            max_y3 = max(all_error_values_ep) + 0.02
            if abs(max_y3 - min_y3) < 0.01:
                center = (min_y3 + max_y3) / 2
                min_y3 = center - 0.005
                max_y3 = center + 0.005
            ax3.set_ylim(min_y3, max_y3)
        else:
            ax3.set_ylim(-0.1, 0.1)
        ax3.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        latest_error_mean = all_loaded_episodes[-1]['mean_error']
        latest_error_std = all_loaded_episodes[-1]['std_error']
        episode_error_text_box.set_text(f"Ep {latest_episode_num} ({selected_feedback_type_name})\nMean: {latest_error_mean:.5f}\nStd Dev: {latest_error_std:.5f}")
        
        episode_impact_means = [d['mean_impact'] for d in all_loaded_episodes]
        episode_impact_stds = [d['std_impact'] for d in all_loaded_episodes]
        episode_impact_means_line.set_data(episode_numbers, episode_impact_means)
        episode_impact_stds_line.set_data(episode_numbers, episode_impact_stds)
        
        all_impact_values_ep = [i for d in all_loaded_episodes for i in d.get('all_impacts_in_episode', [])]
        if all_impact_values_ep:
            min_y5 = min(all_impact_values_ep) - 0.02
            max_y5 = max(all_impact_values_ep) + 0.02
            if abs(max_y5 - min_y5) < 0.01:
                center = (min_y5 + max_y5) / 2
                min_y5 = center - 0.005
                max_y5 = center + 0.005
            ax5.set_ylim(min_y5, max_y5)
        else:
            ax5.set_ylim(-0.1, 0.1)
        ax5.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        latest_impact_mean = all_loaded_episodes[-1]['mean_impact']
        latest_impact_std = all_loaded_episodes[-1]['std_impact']
        episode_impact_text_box.set_text(f"Ep {latest_episode_num} ({selected_feedback_type_name})\nMean: {latest_impact_mean:.5f}\nStd Dev: {latest_impact_std:.5f}")

    else: # 에피소드 데이터가 없으면 그래프 초기화
        episode_means_line.set_data([], [])
        episode_stds_line.set_data([], [])
        episode_maxz_text_box.set_text("No episode data")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 0.3)

        episode_error_means_line.set_data([], [])
        episode_error_stds_line.set_data([], [])
        episode_error_text_box.set_text("No episode data")
        ax3.set_xlim(0, 1)
        ax3.set_ylim(-0.1, 0.1)
        
        episode_impact_means_line.set_data([], [])
        episode_impact_stds_line.set_data([], [])
        episode_impact_text_box.set_text("No episode data")
        ax5.set_xlim(0, 1)
        ax5.set_ylim(-0.1, 0.1)

    fig.canvas.draw_idle() # 그래프 즉시 업데이트


def on_key_press(event):
    """
    키보드 이벤트를 처리하여 trial을 넘기거나 뒤로 돌아갑니다.
    """
    global current_trial_idx, all_loaded_trials, selected_user_folder
    # 여기에 global all_loaded_episodes, selected_feedback_type_subdir, selected_feedback_type_name 추가
    global all_loaded_episodes, selected_feedback_type_subdir, selected_feedback_type_name 

    if event.key == 'right': # 다음 trial
        if not all_loaded_trials:
            print("No trial data loaded. Cannot navigate.")
            return

        if current_trial_idx < len(all_loaded_trials) - 1:
            current_trial_idx += 1
            print(f"Moving to next trial: {current_trial_idx + 1}/{len(all_loaded_trials)}")
            update_plot_with_current_trial()
        else:
            print("Already at the last trial.")
    elif event.key == 'left': # 이전 trial
        if not all_loaded_trials:
            print("No trial data loaded. Cannot navigate.")
            return

        if current_trial_idx > 0:
            current_trial_idx -= 1
            print(f"Moving to previous trial: {current_trial_idx + 1}/{len(all_loaded_trials)}")
            update_plot_with_current_trial()
        else:
            print("Already at the first trial.")
    elif event.key == 'escape': # 뒤로 가기 (폴더 선택 메뉴로)
        print("Exiting current view. Returning to folder selection.")
        plt.close(fig) # 현재 플롯 창 닫기
        
        # 이전 메뉴로 돌아갈 때 전역 변수 초기화
        # 이미 함수 시작 부분에 global로 선언되어 있어야 함.
        all_loaded_trials = []
        all_loaded_episodes = []
        current_trial_idx = -1
        selected_feedback_type_subdir = ""
        selected_feedback_type_name = ""
        
        start_viewer() # 폴더 선택 메뉴 다시 시작
        sys.exit()


def start_viewer():
    """
    뷰어의 시작 지점으로, 사용자에게 폴더를 선택하도록 프롬프트합니다.
    """
    global selected_user_folder, selected_feedback_type_subdir, selected_feedback_type_name

    base_dir = "experiment_data"
    if not os.path.exists(base_dir):
        print(f"Error: '{base_dir}' folder not found. Please run main.py to generate data first.")
        sys.exit(1)

    user_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    if not user_folders:
        print(f"No user folders found in '{base_dir}'. Please run main.py to generate data first.")
        sys.exit(1)

    # 1. 사용자 폴더 선택
    while True:
        print("\n--- Select a User Folder to View Data ---")
        for i, folder in enumerate(user_folders):
            print(f"{i+1}. {folder}")
        print("------------------------------------------")
        print("Enter 'exit' to quit.")

        choice = input("Enter the number of the folder: ").strip()

        if choice.lower() == 'exit':
            print("Exiting viewer.")
            sys.exit(0)

        try:
            folder_idx = int(choice) - 1
            if 0 <= folder_idx < len(user_folders):
                selected_user_folder = os.path.join(base_dir, user_folders[folder_idx])
                print(f"Selected user folder: {selected_user_folder}")
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'exit'.")

    # 2. 피드백 타입 폴더 선택
    feedback_type_options = {}
    for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
        full_path = os.path.join(selected_user_folder, subdir_name)
        if os.path.exists(full_path) and (os.path.exists(os.path.join(full_path, "trials")) or os.path.exists(os.path.join(full_path, "episode_stats"))):
            feedback_type_options[feedback_key] = subdir_name

    if not feedback_type_options:
        print(f"No feedback type data found in '{selected_user_folder}'. Returning to user folder selection.")
        start_viewer() # 데이터가 없으면 사용자 폴더 선택으로 돌아감
        sys.exit() # 현재 스크립트 실행 종료 (start_viewer가 새 인스턴스를 띄울 것이므로)

    feedback_type_list = list(feedback_type_options.keys())
    while True:
        print(f"\n--- Select a Feedback Type from '{os.path.basename(selected_user_folder)}' ---")
        for i, ft in enumerate(feedback_type_list):
            print(f"{i+1}. {ft}")
        print("------------------------------------------")
        print("Enter 'back' to return to user folder selection.")
        print("Enter 'exit' to quit.")

        choice = input("Enter the number of the feedback type: ").strip()

        if choice.lower() == 'exit':
            print("Exiting viewer.")
            sys.exit(0)
        elif choice.lower() == 'back':
            print("Returning to user folder selection.")
            start_viewer() # 사용자 폴더 선택으로 돌아감
            sys.exit() # 현재 스크립트 실행 종료 (start_viewer가 새 인스턴스를 띄울 것이므로)

        try:
            ft_idx = int(choice) - 1
            if 0 <= ft_idx < len(feedback_type_list):
                selected_feedback_type_name = feedback_type_list[ft_idx]
                selected_feedback_type_subdir = feedback_type_options[selected_feedback_type_name]
                print(f"Selected feedback type: {selected_feedback_type_name}")
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number, 'back', or 'exit'.")

    # 모든 데이터 리스트를 초기화하고 선택된 피드백 타입의 데이터만 로드
    global all_loaded_trials, all_loaded_episodes, current_trial_idx
    all_loaded_trials = []
    all_loaded_episodes = []
    current_trial_idx = -1 # 새 데이터 로드 시 인덱스 초기화

    load_data_for_feedback_type(selected_user_folder, selected_feedback_type_name, selected_feedback_type_subdir)

    # Matplotlib 애니메이션 시작 (로드된 데이터가 있을 때만)
    if all_loaded_trials:
        # 애니메이션은 단일 프레임만 업데이트하므로 interval을 큼지막하게 설정
        ani = FuncAnimation(fig, lambda frame: None, interval=1000, blit=False, cache_frame_data=False) # 애니메이션 자체는 dummy, 업데이트는 수동
        fig.canvas.mpl_connect('key_press_event', on_key_press)
        plt.tight_layout()
        plt.show()
    else:
        print("No data available to plot for the selected feedback type. Returning to user folder selection.")
        # 데이터가 없으면 다시 폴더 선택으로 돌아가야 함
        start_viewer() # 사용자 폴더 선택으로 돌아감
        sys.exit() # 현재 스크립트 실행 종료 (start_viewer가 새 인스턴스를 띄울 것이므로)


if __name__ == "__main__":
    start_viewer()