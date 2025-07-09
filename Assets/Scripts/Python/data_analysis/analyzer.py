import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해

# --- Configuration (main.py 및 viewer.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # main.py와 동일하게 설정

# 각 피드백 타입에 할당할 색상 (더 많은 색상이 필요하면 추가)
COLORS = {
    "OnlyVisual": 'blue',
    "OnlyVibrotactile_fixed": 'red',
    "OnlyVibrotactile_adaptive": 'green',
    "VisualwithVibrotactile_fixed": 'purple',
    "VisualwithVibrotactile_adaptive": 'orange',
    "UnknownFeedbackType": 'gray'
}

def load_all_episode_data_for_user(user_folder_path):
    """
    주어진 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 로드합니다.
    """
    all_episode_data = {} # {feedback_type: [episode_entry, ...]}
    
    print(f"Loading all episode data for user: {os.path.basename(user_folder_path)}")

    for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
        episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")
        current_feedback_type_episodes = []

        if os.path.exists(episode_stats_dir):
            episode_files = sorted(glob.glob(os.path.join(episode_stats_dir, 'episode_data_ep*.csv')))
            for e_file_path in episode_files:
                try:
                    df_episode = pd.read_csv(e_file_path)
                    if not df_episode.empty:
                        episode_entry = df_episode.iloc[0].to_dict()
                        
                        # 문자열로 저장된 리스트 파싱 및 float 변환
                        for key_list in ['all_maxZs_in_episode', 'all_errors_in_episode', 'all_impacts_in_episode']:
                            if key_list in episode_entry and isinstance(episode_entry[key_list], str):
                                parsed_list = ast.literal_eval(episode_entry[key_list])
                                episode_entry[key_list] = list(map(float, parsed_list))
                            else:
                                episode_entry[key_list] = [] # 데이터가 없거나 이미 리스트인 경우
                        
                        # float 값 변환
                        for key_float in ['mean_maxZ', 'std_maxZ', 'mean_error', 'std_error', 'mean_impact', 'std_impact']:
                            if key_float in episode_entry:
                                episode_entry[key_float] = float(episode_entry[key_float])

                        # int 값 변환
                        if 'episode_num' in episode_entry:
                            episode_entry['episode_num'] = int(episode_entry['episode_num'])
                        
                        if 'feedback_type' not in episode_entry:
                            episode_entry['feedback_type'] = feedback_key # 파일명에서 유추하거나 기본값 설정

                        current_feedback_type_episodes.append(episode_entry)
                except Exception as e:
                    print(f"Error loading episode file {e_file_path}: {e}")
        
        # 에피소드 번호 기준으로 정렬
        current_feedback_type_episodes.sort(key=lambda x: x['episode_num'])
        
        if current_feedback_type_episodes:
            all_episode_data[feedback_key] = current_feedback_type_episodes
    
    return all_episode_data


def plot_episode_statistics(user_name, episode_data_by_feedback_type):
    """
    각 피드백 조건별 에피소드 통계를 하나의 플롯에 그립니다.
    a. max Z index의 episode 별 mean/variance 변화
    b. error의 episode 별 mean/variance 변화
    c. impact position의 episode 별 변화
    """
    fig, axs = plt.subplots(1, 3, figsize=(25, 8)) # 1행 3열 서브플롯
    fig.suptitle(f'Episode Statistics for {user_name} (Trials per Episode: {TRIALS_PER_EPISODE})', fontsize=18)

    # Subplot 1: Max Z Index Mean and Std Dev
    ax_maxz = axs[0]
    ax_maxz.set_title('Episode Statistics: Max Z Index')
    ax_maxz.set_xlabel("Episode Number")
    ax_maxz.set_ylabel("Max Z Value (m)")
    ax_maxz.grid(True)

    # Subplot 2: Error Mean and Std Dev
    ax_error = axs[1]
    ax_error.set_title('Episode Statistics: Error')
    ax_error.set_xlabel("Episode Number")
    ax_error.set_ylabel("Error (m)")
    ax_error.grid(True)

    # Subplot 3: Impact Position Mean and Std Dev
    ax_impact = axs[2]
    ax_impact.set_title('Episode Statistics: Impact Position')
    ax_impact.set_xlabel("Episode Number")
    ax_impact.set_ylabel("Impact Position (m)")
    ax_impact.grid(True)

    for feedback_type, episodes in episode_data_by_feedback_type.items():
        if not episodes:
            continue
        
        color = COLORS.get(feedback_type, 'gray') # 정의된 색상 사용, 없으면 회색

        episode_nums = [ep['episode_num'] for ep in episodes]
        
        # Max Z
        mean_maxzs = [ep['mean_maxZ'] for ep in episodes]
        std_maxzs = [ep['std_maxZ'] for ep in episodes]
        ax_maxz.plot(episode_nums, mean_maxzs, 'o-', color=color, label=f'{feedback_type} (Mean MaxZ)')
        ax_maxz.fill_between(episode_nums, 
                             np.array(mean_maxzs) - np.array(std_maxzs), 
                             np.array(mean_maxzs) + np.array(std_maxzs), 
                             color=color, alpha=0.2, label=f'{feedback_type} (Std Dev MaxZ)')
        
        # Error
        mean_errors = [ep['mean_error'] for ep in episodes]
        std_errors = [ep['std_error'] for ep in episodes]
        ax_error.plot(episode_nums, mean_errors, 'o-', color=color, label=f'{feedback_type} (Mean Error)')
        ax_error.fill_between(episode_nums, 
                             np.array(mean_errors) - np.array(std_errors), 
                             np.array(mean_errors) + np.array(std_errors), 
                             color=color, alpha=0.2, label=f'{feedback_type} (Std Dev Error)')

        # Impact Position
        mean_impacts = [ep['mean_impact'] for ep in episodes]
        std_impacts = [ep['std_impact'] for ep in episodes]
        ax_impact.plot(episode_nums, mean_impacts, 'o-', color=color, label=f'{feedback_type} (Mean Impact Pos)')
        ax_impact.fill_between(episode_nums, 
                               np.array(mean_impacts) - np.array(std_impacts), 
                               np.array(mean_impacts) + np.array(std_impacts), 
                               color=color, alpha=0.2, label=f'{feedback_type} (Std Dev Impact Pos)')

    # 범례는 각 서브플롯에 하나씩
    ax_maxz.legend(loc='best')
    ax_error.legend(loc='best')
    ax_impact.legend(loc='best')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # 타이틀 공간 확보
    plt.show()


def start_analyzer():
    """
    분석기의 시작 지점으로, 사용자에게 폴더를 선택하도록 프롬프트합니다.
    """
    base_dir = "Python/data_analysis/experiment_data"
    if not os.path.exists(base_dir):
        print(f"Error: '{base_dir}' folder not found. Please ensure data has been collected by main.py.")
        sys.exit(1)

    user_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    if not user_folders:
        print(f"No user folders found in '{base_dir}'. Please ensure data has been collected by main.py.")
        sys.exit(1)

    while True:
        print("\n--- Select a User Folder to Analyze Data ---")
        for i, folder in enumerate(user_folders):
            print(f"{i+1}. {folder}")
        print("------------------------------------------")
        print("Enter 'exit' to quit.")

        choice = input("Enter the number of the folder: ").strip()

        if choice.lower() == 'exit':
            print("Exiting analyzer.")
            sys.exit(0)

        try:
            folder_idx = int(choice) - 1
            if 0 <= folder_idx < len(user_folders):
                selected_user_name = user_folders[folder_idx]
                selected_user_folder_path = os.path.join(base_dir, selected_user_name)
                print(f"Selected user folder: {selected_user_name}")
                
                # 선택된 사용자 폴더의 모든 피드백 타입 데이터 로드
                episode_data = load_all_episode_data_for_user(selected_user_folder_path)
                
                if not episode_data:
                    print(f"No episode data found for user '{selected_user_name}'. Please choose another user or collect more data.")
                    continue # 다시 사용자 선택 메뉴로
                
                # 로드된 데이터 플롯
                plot_episode_statistics(selected_user_name, episode_data)
                
                # 플롯이 닫히면 사용자 선택 메뉴로 돌아감
                print("Plot closed. Returning to user folder selection.")
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'exit'.")

if __name__ == "__main__":
    start_analyzer()