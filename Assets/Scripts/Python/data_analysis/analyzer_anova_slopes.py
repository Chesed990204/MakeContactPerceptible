import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import pingouin as pg # pingouin 라이브러리 임포트

# --- Configuration ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15
FINAL_EPISODE_NUM = 4 # ANOVA에 사용할 기울기 값의 에피소드 번호

def load_and_calculate_slopes_for_anova(base_data_dir):
    """
    모든 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 로드하고,
    각 사용자의 각 조건별 최종 에피소드 (FINAL_EPISODE_NUM)의 기울기를 계산하여
    ANOVA에 적합한 DataFrame으로 반환합니다.
    """
    all_slope_data = []
    
    user_folders = sorted([f for f in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, f))])

    if not user_folders:
        print(f"No user folders found in '{base_data_dir}'. Please ensure data has been collected by main.py.")
        return pd.DataFrame()

    print(f"Loading data and calculating slopes for ANOVA from: {base_data_dir}")

    # 사용자 폴더 이름을 "User 1", "User 2" 등으로 매핑
    user_name_mapping = {folder_name: f"User {i+1}" for i, folder_name in enumerate(user_folders)}

    # 각 측정항목별 원본 데이터 키
    data_keys = {
        'Mean MaxZ Slope': 'mean_maxZ',
        'Std Dev MaxZ Slope': 'std_maxZ',
        'Mean Error Slope': 'mean_error',
        'Std Dev Error Slope': 'std_error',
        # Impact Position 기울기는 ANOVA에서 제외되므로 여기에 추가하지 않습니다.
    }

    for user_folder_name in user_folders:
        user_folder_path = os.path.join(base_data_dir, user_folder_name)
        display_user_name = user_name_mapping[user_folder_name]

        for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
            episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")

            if os.path.exists(episode_stats_dir):
                episode_files = sorted(glob.glob(os.path.join(episode_stats_dir, 'episode_data_ep*.csv')))
                
                # 이 피드백 타입/사용자에 대한 모든 에피소드 데이터 로드
                df_episodes_for_user_ft = []
                for e_file_path in episode_files:
                    try:
                        df_episode = pd.read_csv(e_file_path)
                        if not df_episode.empty:
                            entry = df_episode.iloc[0].to_dict()
                            entry['episode_num'] = int(entry['episode_num'])
                            df_episodes_for_user_ft.append(entry)
                    except Exception as e:
                        print(f"  Error loading episode file {e_file_path}: {e}")
                
                df_user_ft = pd.DataFrame(df_episodes_for_user_ft).sort_values(by='episode_num')

                if df_user_ft.empty:
                    continue
                
                # 필요한 에피소드 번호까지의 데이터만 사용
                episode_nums = df_user_ft['episode_num'].tolist()

                # FINAL_EPISODE_NUM이 실제 에피소드 목록에 있는지 확인
                if FINAL_EPISODE_NUM not in episode_nums:
                    # print(f"  Warning: User {display_user_name}, feedback {feedback_key} does not have episode {FINAL_EPISODE_NUM}. Skipping.")
                    continue

                # 각 지표에 대한 기울기 계산
                for slope_type, original_data_key in data_keys.items():
                    values = df_user_ft[original_data_key].tolist()
                    slopes = [calculate_slope(episode_nums[:i+1], values[:i+1]) for i in range(len(episode_nums))]
                    
                    # FINAL_EPISODE_NUM에 해당하는 기울기 값 추출
                    idx = episode_nums.index(FINAL_EPISODE_NUM)
                    final_slope_value = slopes[idx]
                    
                    if not np.isnan(final_slope_value):
                        all_slope_data.append({
                            'user_id': display_user_name,
                            'feedback_type': feedback_key,
                            'slope_type': slope_type,
                            'slope_value': final_slope_value
                        })
    
    df_slopes = pd.DataFrame(all_slope_data)
    if not df_slopes.empty:
        df_slopes['feedback_type'] = df_slopes['feedback_type'].astype('category')
        df_slopes['slope_type'] = df_slopes['slope_type'].astype('category')
        df_slopes['user_id'] = df_slopes['user_id'].astype('category')
    
    return df_slopes

def calculate_slope(x_values, y_values):
    """
    선형 회귀를 사용하여 기울기를 계산합니다.
    """
    if len(x_values) < 2:
        return np.nan # 데이터 포인트가 2개 미만이면 기울기 계산 불가
    
    coefficients = np.polyfit(x_values, y_values, 1)
    return coefficients[0]


def perform_anova_on_slopes(df_slopes):
    """
    계산된 기울기 데이터프레임에 대해 ANOVA 분석을 수행합니다.
    """
    if df_slopes.empty:
        print("No slope data available for ANOVA analysis.")
        return

    print("\n--- Performing ANOVA on Slopes ---")

    # 각 slope_type (예: 'Mean MaxZ Slope')별로 개별 ANOVA 수행
    for slope_type_val in df_slopes['slope_type'].unique():
        print(f"\n===== Analyzing Slope Type: {slope_type_val} =====")
        
        df_filtered = df_slopes[df_slopes['slope_type'] == slope_type_val].copy()

        # One-Way ANOVA (Feedback Type)
        # 기울기 값은 각 사용자의 최종 에피소드에 대한 값으로, 반복 측정이 아니므로 One-Way ANOVA가 적합합니다.
        # subject factor가 있다면, Mixed ANOVA를 고려해야 합니다.
        # 여기서는 feedback_type 간의 차이만 봅니다.
        print("\n--- One-Way ANOVA (Pingouin) by Feedback Type for this Slope Type ---")
        try:
            aov_ow = pg.anova(data=df_filtered, dv='slope_value', between='feedback_type', detailed=True)
            print(aov_ow)
            print(f"Interpretation: If p-val for 'feedback_type' is < 0.05, there's a significant difference in {slope_type_val} between feedback types.")
        except Exception as e:
            print(f"  Error performing One-Way ANOVA for {slope_type_val}: {e}")
            print("  (Common issues: not enough data points per group, or no variance within groups)")

        # Mixed ANOVA (Feedback Type as Between-Subjects, User as Random Effect)
        # 만약 'user_id'를 random effect로 다루고 싶다면 Mixed ANOVA 또는 Linear Mixed Model을 사용합니다.
        # pingouin의 `mixed_anova`는 하나의 within-subject factor와 하나의 between-subject factor를 다룹니다.
        # 여기서는 `feedback_type`이 between-subject이고, `user_id`는 subject 자체이므로, 
        # pingouin의 `anova` 함수가 사용자들을 독립적인 관측치로 다루는 것이 됩니다.
        # 만약 모든 사용자가 모든 피드백 타입을 경험했다면, 'user_id'가 Subject이고 'feedback_type'이 Within-Subject Factor인 Repeated Measures ANOVA가 더 적절할 수 있습니다.
        # 하지만 기울기 데이터는 각 사용자의 각 피드백 타입당 하나의 값만을 가지고 있으므로, Repeated Measures ANOVA는 불가능합니다.
        # 즉, 각 사용자마다 각 feedback_type에 대한 하나의 slope_value가 있으므로, 이 경우 user_id는 Subject이고 feedback_type은 Within-Subject factor가 됩니다.
        # 이를 위해 데이터를 wide format으로 변환해야 합니다.

        print(f"\n--- Repeated Measures ANOVA (Pingouin) for {slope_type_val} by Feedback Type (User as Subject) ---")
        try:
            # RM ANOVA를 위해 데이터를 Wide format으로 변환 (user_id를 인덱스로, feedback_type을 컬럼으로)
            df_wide_rm = df_filtered.pivot_table(index='user_id', columns='feedback_type', values='slope_value')
            # 컬럼 이름 평탄화는 필요 없음 (feedback_type이 이미 단일 레벨)
            
            # rm_anova의 dv 인자에 pivot된 데이터의 모든 컬럼 이름을 전달
            rm_dv_cols = list(df_wide_rm.columns)

            if len(rm_dv_cols) < 2:
                print(f"  Warning: Not enough feedback types (columns) for RM ANOVA for {slope_type_val}. Skipping.")
                continue
            
            aov_rm = pg.rm_anova(data=df_wide_rm, dv=rm_dv_cols, 
                                 within='feedback_type', # feedback_type이 within-subject factor
                                 subject='user_id', detailed=True, correction=True)
            print(aov_rm)
            print(f"Interpretation: If p-val for 'feedback_type' is < 0.05, there's a significant difference in {slope_type_val} between feedback types (within-subjects).")

        except Exception as e:
            print(f"  Error performing Repeated Measures ANOVA for {slope_type_val}: {e}")
            print("  (Common issues: Data imbalance, missing values for subject-condition combinations, or not enough unique subjects/feedback types.)")
            print("  Ensure each subject has a slope value for ALL feedback types for this analysis.")


def start_slope_anova_analyzer():
    """
    모든 사용자의 데이터를 로드하고 기울기를 계산한 후, ANOVA를 수행하는 메인 함수.
    """
    # 데이터 경로를 현재 스크립트 위치 기준으로 설정 (Git 리포지토리 구조를 고려)
    # analyzer_all_users_slopes_with_mean.py는 Assets/Scripts/Python/data_analysis에 있다고 가정
    # experiment_data는 Assets/Scripts/Python/data_analysis/experiment_data에 있다고 가정
    base_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment_data") 

    df_slopes_for_anova = load_and_calculate_slopes_for_anova(base_data_dir)
    
    if not df_slopes_for_anova.empty:
        perform_anova_on_slopes(df_slopes_for_anova)
    else:
        print("No slope data loaded for ANOVA analysis. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    start_slope_anova_analyzer()