import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import statsmodels.api as sm # ANOVA 및 LMM
from statsmodels.formula.api import ols # OLS for One-Way ANOVA formula
from statsmodels.stats.anova import anova_lm # ANOVA table for OLS

# --- Configuration (main.py 및 viewer.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)

def load_all_episode_data_for_anova(base_data_dir):
    """
    모든 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 통합하여 로드합니다.
    ANOVA 분석을 위해 단일 DataFrame으로 반환합니다.
    """
    all_combined_data = []
    
    user_folders = [f for f in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, f))]

    if not user_folders:
        print(f"No user folders found in '{base_data_dir}'. Please ensure data has been collected by main.py.")
        return pd.DataFrame()

    print(f"Loading all episode data from: {base_data_dir}")

    for user_folder_name in user_folders:
        user_folder_path = os.path.join(base_data_dir, user_folder_name)
        
        for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
            episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")

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
                            
                            # 사용자 ID와 피드백 타입 추가 (이미 있을 수 있지만 다시 확인)
                            episode_entry['user_id'] = user_folder_name
                            episode_entry['feedback_type'] = feedback_key

                            all_combined_data.append(episode_entry)
                    except Exception as e:
                        print(f"Error loading episode file {e_file_path}: {e}")
    
    df = pd.DataFrame(all_combined_data)
    # 데이터가 로드되면 episode_num과 feedback_type을 범주형으로 변환
    if not df.empty:
        df['episode_num'] = df['episode_num'].astype('category')
        df['feedback_type'] = df['feedback_type'].astype('category')
        df['user_id'] = df['user_id'].astype('category')
        df = df.sort_values(by=['user_id', 'feedback_type', 'episode_num']).reset_index(drop=True)
    
    return df


def perform_anova_analysis(df):
    """
    로드된 DataFrame에 대해 ANOVA 분석을 수행합니다.
    """
    if df.empty:
        print("No data available for ANOVA analysis.")
        return

    dependent_variables = [
        'mean_maxZ', 'std_maxZ', 'mean_error', 'std_error', 'mean_impact', 'std_impact'
    ]

    print("\n--- Performing ANOVA Analysis ---")

    for dep_var in dependent_variables:
        print(f"\n===== Analyzing Dependent Variable: {dep_var} =====")
        
        # 1. One-Way ANOVA (Feedback Type)
        # 모든 에피소드 데이터를 한 번에 사용하여 feedback_type 간의 차이를 봅니다.
        # 동일 사용자로부터의 반복 측정 데이터를 고려하지 않으므로, 유의성에 대한 해석에 주의가 필요합니다.
        print("\n--- One-Way ANOVA by Feedback Type ---")
        try:
            # formula = f'{dep_var} ~ C(feedback_type)'
            # C()는 변수가 범주형임을 명시
            model_ow = ols(f'{dep_var} ~ C(feedback_type)', data=df).fit()
            anova_results_ow = anova_lm(model_ow)
            print(anova_results_ow)
            print(f"Interpretation: If Pr(>F) for C(feedback_type) is < 0.05, there's a significant difference between feedback types for {dep_var}.")
        except Exception as e:
            print(f"  Error performing One-Way ANOVA for {dep_var}: {e}")
            print("  (Often occurs if a feedback type has too few data points or no variance)")

        # 2. Linear Mixed-Effects Model (LMM) - More appropriate for repeated measures
        # user_id를 무선 효과(random effect)로 포함하여 사용자 간의 개별적인 차이를 모델링합니다.
        # feedback_type과 episode_num을 고정 효과(fixed effects)로 포함합니다.
        print(f"\n--- Linear Mixed-Effects Model for {dep_var} (Fixed: Feedback Type, Episode Num; Random: User) ---")
        try:
            # 종속 변수 ~ 고정효과 + (1|무선효과)
            # 고정 효과 간의 상호작용 (feedback_type * episode_num)도 포함할 수 있습니다.
            # 하지만 모델이 너무 복잡해지면 수렴 문제가 발생할 수 있으므로, 단순한 모델부터 시작합니다.
            model_lmm = sm.MixedLM.from_formula(f"{dep_var} ~ C(feedback_type) * C(episode_num)",
                                                data=df,
                                                groups=df['user_id']).fit()
            print(model_lmm.summary())
            print(f"Interpretation: Look at P>|t| values for C(feedback_type), C(episode_num), and their interaction (C(feedback_type):C(episode_num)).")
            print(f"  P>|t| < 0.05 indicates a significant effect for {dep_var}.")
            print("  A significant interaction suggests the effect of feedback type depends on episode progression.")
        except Exception as e:
            print(f"  Error performing LMM for {dep_var}: {e}")
            print("  (Common issues: not enough data points per group/combination, or model complexity)")
            print("  If you encounter convergence warnings, consider simplifying the model (e.g., remove interaction term).")


def start_anova_analyzer():
    """
    ANOVA 분석기의 시작 지점으로, 데이터를 로드하고 분석을 수행합니다.
    """
    base_data_dir = "Python/data_analysis/experiment_data" # 데이터가 있는 최상위 폴더 경로

    # Matplotlib 한글 폰트 설정 (Mac 환경에서 필요하다면 주석 해제 및 설정)
    # import matplotlib.font_manager as fm
    # plt.rcParams['font.family'] = 'AppleGothic' # 또는 'NanumGothic', 'Apple SD Gothic Neo' 등
    # plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

    df_for_anova = load_all_episode_data_for_anova(base_data_dir)
    
    if not df_for_anova.empty:
        perform_anova_analysis(df_for_anova)
    else:
        print("Exiting ANOVA analyzer due to no data.")
        sys.exit(0)

if __name__ == "__main__":
    start_anova_analyzer()