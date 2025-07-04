import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon, shapiro

DATA_DIRS = {
    "bare_hand": "Python\\hand_data\\bare_hand",
}

# 조건별 maxZ 값 저장
condition_trials = {cond: [] for cond in DATA_DIRS.keys()}

# CSV 파일 읽기 (기존 wilcoxon_analysis.py와 동일)
for cond, path in DATA_DIRS.items():
    csv_files = sorted(glob.glob(os.path.join(path, "*.csv"))) # 파일 순서가 trial 순서를 반영한다고 가정
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "maxZ" in df.columns:
                condition_trials[cond].append(df["maxZ"].max())
            else:
                print(f"'maxZ' column not found in {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

# bare_hand 조건의 maxZ 데이터 추출
bare_hand_maxZ = condition_trials["bare_hand"]

GROUND_TRUTH = 0.1293

# 가설 2: 맨손(bare_hand)으로 가상 버튼 상호작용 시, 사용자의 `maxZ` 값은 초기 시행(trial)에서 넓은 분포를 보이다가 점차 수렴하는 경향을 보일 것이다.

print("\n--- 가설 2 분석: bare_hand maxZ 값의 수렴 경향 ---")

if len(bare_hand_maxZ) == 0:
    print(" bare_hand 데이터가 부족하여 가설 2를 분석할 수 없습니다.")
else:
    # 데이터 분할 (초기 25% vs 후기 25% 비교)
    num_trials = len(bare_hand_maxZ)
    if num_trials < 4:
        print(" 최소 4개 이상의 trial 데이터가 필요하여 초기/후기 구간 분석이 어렵습니다.")
    else:
        early_trials_idx = int(num_trials * 0.25)
        late_trials_idx = int(num_trials * 0.75)

        early_maxZ = bare_hand_maxZ[:early_trials_idx]
        late_maxZ = bare_hand_maxZ[late_trials_idx:]

        if len(early_maxZ) > 1 and len(late_maxZ) > 1:
            std_early = np.std(early_maxZ)
            std_late = np.std(late_maxZ)

            print(f" 전체 bare_hand trial 수: {num_trials}")
            print(f" 초기 {len(early_maxZ)}개 trial의 표준편차: {std_early:.5f}")
            print(f" 후기 {len(late_maxZ)}개 trial의 표준편차: {std_late:.5f}")

            if std_late < std_early:
                print(" → 후기 trial의 표준편차가 초기 trial보다 낮아, 수렴 경향을 시사합니다.")
            else:
                print(" → 후기 trial의 표준편차가 초기 trial보다 높거나 비슷하여, 수렴 경향이 뚜렷하지 않습니다.")

            # 시계열 그래프
            plt.figure(figsize=(10, 5))
            plt.plot(bare_hand_maxZ, marker='o', linestyle='-', markersize=4, color='skyblue')
            plt.title('Bare Hand MaxZ Over Trials')
            plt.xlabel('Trial Number')
            plt.ylabel('MaxZ Value')
            plt.grid(True)
            plt.axhline(y=GROUND_TRUTH, color='r', linestyle='--', label='GROUND_TRUTH')
            plt.legend()
            plt.tight_layout()
            plt.savefig('bare_hand_maxZ_convergence.png') # 이미지 파일로 저장

        else:
            print(" 초기 또는 후기 구간의 trial 수가 충분하지 않아 표준편차를 계산할 수 없습니다.")


