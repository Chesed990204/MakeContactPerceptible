import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import datetime # 파일명에 타임스탬프 추가

# --- Configuration (main.py 및 viewer.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)

# 각 피드백 타입에 할당할 색상 (더 많은 색상이 필요하면 추가)
COLORS = {
    "OnlyVisual": 'blue',
    "OnlyVibrotactile_fixed": 'red',
    "OnlyVibrotactile_adaptive": 'green',
    "VisualwithVibrotactile_fixed": 'purple',
    "VisualwithVibrotactile_adaptive": 'orange',
    "UnknownFeedbackType": 'gray'
}

# 기울기 플롯을 위한 선 스타일 및 마커
MEAN_SLOPE_LINESTYLE = '-'
MEAN_SLOPE_MARKER = 'o'
STD_SLOPE_LINESTYLE = '--'
STD_SLOPE_MARKER = 'x'

# 수렴 확인 대상 조건
CONVERGENCE_CONDITION = "VisualwithVibrotactile_adaptive"
HIGHLIGHT_LINEWIDTH = 3 # 강조할 선의 두께
NORMAL_LINEWIDTH = 1.5 # 일반 선의 두께

# 저장 폴더 이름
SAVE_DIR_NAME = "analysis_plots"

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
                            # 'episode_num'이 문자열일 경우 int로 변환
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

def calculate_slope(x_values, y_values):
    """
    선형 회귀를 사용하여 기울기를 계산합니다.
    """
    if len(x_values) < 2:
        return np.nan # 데이터 포인트가 2개 미만이면 기울기 계산 불가
    
    # 1차 다항식(직선)을 x, y 값에 맞춥니다. coefficients[0]이 기울기입니다.
    coefficients = np.polyfit(x_values, y_values, 1)
    return coefficients[0]


def plot_episode_statistics_combined_slopes(user_name, episode_data_by_feedback_type):
    """
    각 피드백 조건별 에피소드 통계를 하나의 플롯에 그리고,
    Max Z, Error, Impact Position의 평균/표준편차를 표시합니다.
    추가로 Max Z와 Error에 대해서는 평균과 표준 편차의 기울기를 하나의 플롯에 함께 표시합니다.
    'VisualwithVibrotactile_adaptive' 조건을 강조하고 해당 기울기 값을 출력합니다.
    """
    fig, axs = plt.subplots(2, 3, figsize=(25, 15)) # 2행 3열 서브플롯
    fig.suptitle(f'Episode Statistics for {user_name} (Trials per Episode: {TRIALS_PER_EPISODE})', fontsize=18)

    # Subplot (0,0): Max Z Index Mean and Std Dev
    ax_maxz_mean_std = axs[0, 0]
    ax_maxz_mean_std.set_title('Episode Statistics: Max Z Index (Mean & Std Dev)')
    ax_maxz_mean_std.set_xlabel("Episode Number")
    ax_maxz_mean_std.set_ylabel("Max Z Value (m)")
    ax_maxz_mean_std.grid(True)

    # Subplot (0,1): Error Mean and Std Dev
    ax_error_mean_std = axs[0, 1]
    ax_error_mean_std.set_title('Episode Statistics: Error (Mean & Std Dev)')
    ax_error_mean_std.set_xlabel("Episode Number")
    ax_error_mean_std.set_ylabel("Error (m)")
    ax_error_mean_std.grid(True)
    
    # Subplot (0,2): Impact Position Mean and Std Dev
    ax_impact_mean_std = axs[0, 2]
    ax_impact_mean_std.set_title('Episode Statistics: Impact Position (Mean & Std Dev)')
    ax_impact_mean_std.set_xlabel("Episode Number")
    ax_impact_mean_std.set_ylabel("Impact Position (m)")
    ax_impact_mean_std.grid(True)

    # Subplot (1,0): Max Z Index Mean & Std Dev Slopes (COMBINED PLOT)
    ax_maxz_slopes = axs[1, 0]
    ax_maxz_slopes.set_title('Max Z Slopes (Mean & Std Dev)')
    ax_maxz_slopes.set_xlabel("Episode Number")
    ax_maxz_slopes.set_ylabel("Slope Value")
    ax_maxz_slopes.grid(True)

    # Subplot (1,1): Error Mean & Std Dev Slopes (COMBINED PLOT)
    ax_error_slopes = axs[1, 1]
    ax_error_slopes.set_title('Error Slopes (Mean & Std Dev)')
    ax_error_slopes.set_xlabel("Episode Number")
    ax_error_slopes.set_ylabel("Slope Value")
    ax_error_slopes.grid(True)

    # Subplot (1,2) for Impact Position Slopes (can be left empty or used for other info)
    axs[1, 2].set_visible(False)

    print(f"\n--- Convergence Analysis for '{CONVERGENCE_CONDITION}' ---")

    for feedback_type, episodes in episode_data_by_feedback_type.items():
        if not episodes:
            continue
        
        color = COLORS.get(feedback_type, 'gray')
        
        # 강조 여부 결정
        lw = HIGHLIGHT_LINEWIDTH if feedback_type == CONVERGENCE_CONDITION else NORMAL_LINEWIDTH
        alpha_fill = 0.4 if feedback_type == CONVERGENCE_CONDITION else 0.2

        episode_nums = [ep['episode_num'] for ep in episodes]
        
        # Max Z Mean and Std Dev
        mean_maxzs = [ep['mean_maxZ'] for ep in episodes]
        std_maxzs = [ep['std_maxZ'] for ep in episodes]
        ax_maxz_mean_std.plot(episode_nums, mean_maxzs, 'o-', color=color, label=f'{feedback_type} (Mean MaxZ)', linewidth=lw)
        ax_maxz_mean_std.fill_between(episode_nums, 
                                      np.array(mean_maxzs) - np.array(std_maxzs), 
                                      np.array(mean_maxzs) + np.array(std_maxzs), 
                                      color=color, alpha=alpha_fill, label=f'{feedback_type} (Std Dev MaxZ)')
        
        # Max Z Slopes (Combined)
        maxz_mean_slopes = [calculate_slope(episode_nums[:i+1], mean_maxzs[:i+1]) for i in range(len(episode_nums))]
        maxz_std_slopes = [calculate_slope(episode_nums[:i+1], std_maxzs[:i+1]) for i in range(len(episode_nums))]
        ax_maxz_slopes.plot(episode_nums, maxz_mean_slopes, MEAN_SLOPE_LINESTYLE + MEAN_SLOPE_MARKER, 
                            color=color, label=f'{feedback_type} Mean Slope', linewidth=lw)
        ax_maxz_slopes.plot(episode_nums, maxz_std_slopes, STD_SLOPE_LINESTYLE + STD_SLOPE_MARKER, 
                            color=color, label=f'{feedback_type} Std Dev Slope', linewidth=lw)


        # Error Mean and Std Dev
        mean_errors = [ep['mean_error'] for ep in episodes]
        std_errors = [ep['std_error'] for ep in episodes]
        ax_error_mean_std.plot(episode_nums, mean_errors, 'o-', color=color, label=f'{feedback_type} (Mean Error)', linewidth=lw)
        ax_error_mean_std.fill_between(episode_nums, 
                                       np.array(mean_errors) - np.array(std_errors), 
                                       np.array(mean_errors) + np.array(std_errors), 
                                       color=color, alpha=alpha_fill, label=f'{feedback_type} (Std Dev Error)')

        # Error Slopes (Combined)
        error_mean_slopes = [calculate_slope(episode_nums[:i+1], mean_errors[:i+1]) for i in range(len(episode_nums))]
        error_std_slopes = [calculate_slope(episode_nums[:i+1], std_errors[:i+1]) for i in range(len(episode_nums))]
        ax_error_slopes.plot(episode_nums, error_mean_slopes, MEAN_SLOPE_LINESTYLE + MEAN_SLOPE_MARKER, 
                             color=color, label=f'{feedback_type} Mean Slope', linewidth=lw)
        ax_error_slopes.plot(episode_nums, error_std_slopes, STD_SLOPE_LINESTYLE + STD_SLOPE_MARKER, 
                             color=color, label=f'{feedback_type} Std Dev Slope', linewidth=lw)

        # Impact Position Mean and Std Dev
        mean_impacts = [ep['mean_impact'] for ep in episodes]
        std_impacts = [ep['std_impact'] for ep in episodes]
        ax_impact_mean_std.plot(episode_nums, mean_impacts, 'o-', color=color, label=f'{feedback_type} (Mean Impact Pos)', linewidth=lw)
        ax_impact_mean_std.fill_between(episode_nums, 
                                        np.array(mean_impacts) - np.array(std_impacts), 
                                        np.array(mean_impacts) + np.array(std_impacts), 
                                        color=color, alpha=alpha_fill, label=f'{feedback_type} (Std Dev Impact Pos)')

        # 특정 조건의 마지막 기울기 값 출력
        if feedback_type == CONVERGENCE_CONDITION:
            if len(maxz_mean_slopes) > 1 and not np.isnan(maxz_mean_slopes[-1]):
                print(f"  {feedback_type} - Max Z Mean Slope (Last): {maxz_mean_slopes[-1]:.6f}")
            else:
                print(f"  {feedback_type} - Max Z Mean Slope: Not enough data for slope.")

            if len(maxz_std_slopes) > 1 and not np.isnan(maxz_std_slopes[-1]):
                print(f"  {feedback_type} - Max Z Std Dev Slope (Last): {maxz_std_slopes[-1]:.6f}")
            else:
                print(f"  {feedback_type} - Max Z Std Dev Slope: Not enough data for slope.")

            if len(error_mean_slopes) > 1 and not np.isnan(error_mean_slopes[-1]):
                print(f"  {feedback_type} - Error Mean Slope (Last): {error_mean_slopes[-1]:.6f}")
            else:
                print(f"  {feedback_type} - Error Mean Slope: Not enough data for slope.")

            if len(error_std_slopes) > 1 and not np.isnan(error_std_slopes[-1]):
                print(f"  {feedback_type} - Error Std Dev Slope (Last): {error_std_slopes[-1]:.6f}")
            else:
                print(f"  {feedback_type} - Error Std Dev Slope: Not enough data for slope.")

    # 범례는 각 서브플롯에 하나씩
    ax_maxz_mean_std.legend(loc='best')
    ax_error_mean_std.legend(loc='best')
    ax_impact_mean_std.legend(loc='best')
    ax_maxz_slopes.legend(loc='best')
    ax_error_slopes.legend(loc='best')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # 타이틀 공간 확보
    
    # --- 플롯 저장 기능 추가 ---
    print("\nDEBUG: Preparing to save plot.")
    save_dir = os.path.join("Python/data_analysis/experiment_data", user_name, SAVE_DIR_NAME)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_name}_episode_analysis_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    try:
        plt.savefig(filepath, dpi=300, bbox_inches='tight') # 고해상도, 잘림 방지
        print(f"\nPlot saved successfully to: {filepath}")
    except Exception as e:
        print(f"\nError saving plot: {e}")
    # --- 저장 기능 끝 ---

    plt.show() # 저장 후에도 화면에 플롯 표시


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
                
                # 로드된 데이터 플롯 (기울기 포함)
                plot_episode_statistics_combined_slopes(selected_user_name, episode_data)
                
                # 플롯이 닫히면 사용자 선택 메뉴로 돌아감
                print("Plot closed. Returning to user folder selection.")
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'exit'.")

if __name__ == "__main__":
    start_analyzer()