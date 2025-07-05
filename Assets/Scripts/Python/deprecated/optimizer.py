import numpy as np
from scipy.optimize import minimize

# 1. 목적 함수 정의
def objective(x, mu_V, sigma_V_sq, mu_target, alpha, beta):
    """
    최적화할 목적 함수: 혼합 분포의 평균 목표 근접성 및 분산 최소화.
    x = [impact_position (p), 시각적 단서 가중치 (w_V), 진동 촉각 단서 가중치 (w_T)]
    """
    p, w_V, w_T = x
    
    # 혼합 평균 계산
    # 진동 촉각 피드백의 평균은 impact_position (p)입니다.
    mu_mixture = w_V * mu_V + w_T * p
    
    # 혼합 분산 계산 (진동 촉각 피드백은 Dirac delta로 가정하여 sigma_T_sq = 0)
    # sigma_T_sq = 0, mu_T = p
    sigma2_mixture = w_V * (sigma_V_sq + mu_V**2) + w_T * (p**2) - (mu_mixture)**2
    
    # 두 목표를 결합한 최종 목적 함수
    # alpha, beta는 각 목표의 상대적 중요도를 나타내는 가중치
    obj_val = alpha * (mu_mixture - mu_target)**2 + beta * sigma2_mixture
    return obj_val

# 2. 제약 조건 정의
# 등식 제약: w_V + w_T = 1
def eq_constraint(x):
    """혼합 가중치의 합이 1이 되도록 하는 등식 제약."""
    p, w_V, w_T = x
    return w_V + w_T - 1.0

# 최적화 실행 함수
def run_adaptive_impact_position_optimizer(episode_data, mu_target, alpha=1.0, beta=1.0):
    """
    주어진 에피소드 데이터를 기반으로 impact_position을 최적화합니다.
    """
    # 에피소드 데이터에서 시각적 단서(button_displacement)의 평균과 분산 계산
    mu_V = np.mean(episode_data)
    sigma_V_sq = np.var(episode_data)
    
    print(f"--- 에피소드 데이터 통계 ---")
    print(f"  시각적 단서 평균 (mu_V): {mu_V:.4f}")
    print(f"  시각적 단서 분산 (sigma_V_sq): {sigma_V_sq:.4f}")
    print(f"  혼합 분포 목표 평균 (mu_target): {mu_target:.4f}")

    # 변수 (p, w_V, w_T)에 대한 경계 정의
    # p_min과 p_max는 시각적 단서의 물리적 변위 범위에 기반합니다.
    p_min = 0.0
    p_max = 0.1293
    bounds = [(p_min, p_max), (0.0, 1.0), (0.0, 1.0)] # p, w_V, w_T의 경계
    
    # 제약 조건 목록
    constraints = [{'type': 'eq', 'fun': eq_constraint}]

    # 다중 시작 최적화 설정
    num_restarts = 50 # 무작위 초기 추정 횟수 (더 많을수록 전역 최적해 찾을 가능성 증가, 계산 비용 증가)
    best_obj_val = np.inf
    best_solution = None

    print(f"\n--- 다중 시작 최적화 시작 ({num_restarts}회 재시작) ---")

    for i in range(num_restarts):
        # 경계 내에서 무작위 초기 추정값 생성
        p_init = np.random.uniform(p_min, p_max)
        w_init_raw = np.random.rand(2)
        w_V_init, w_T_init = w_init_raw / np.sum(w_init_raw) # 합이 1이 되도록 정규화
        x0 = [p_init, w_V_init, w_T_init]
        
        try:
            # SLSQP 메서드를 사용하여 최적화 실행 (비선형 제약 조건 처리에 적합)
            res = minimize(objective, x0, args=(mu_V, sigma_V_sq, mu_target, alpha, beta),
                           method='SLSQP', bounds=bounds, constraints=constraints)
            
            if res.success:
                if res.fun < best_obj_val:
                    best_obj_val = res.fun
                    best_solution = res.x
                # 선택 사항: 각 재시작의 진행 상황 출력
                # print(f"  재시작 {i+1}: 성공={res.success}, 목적 함수 값={res.fun:.4f}, 해={res.x}")
                
        except Exception as e:
            print(f"  재시작 {i+1}: 최적화 중 오류 발생: {e}")

    if best_solution is not None:
        optimal_p, optimal_w_V, optimal_w_T = best_solution
        
        # 최종 혼합 특성 재계산 (보고용)
        final_mu_mixture = optimal_w_V * mu_V + optimal_w_T * optimal_p
        final_sigma2_mixture = optimal_w_V * (sigma_V_sq + mu_V**2) + optimal_w_T * (optimal_p**2) - (final_mu_mixture)**2
        
        print("\n--- 최적화 완료 ---")
        print(f"최적의 Impact Position (p): {optimal_p:.4f}")
        print(f"최적의 시각적 단서 가중치 (w_V): {optimal_w_V:.4f}")
        print(f"최적의 진동 촉각 단서 가중치 (w_T): {optimal_w_T:.4f}")
        print(f"달성된 혼합 평균: {final_mu_mixture:.4f}")
        print(f"달성된 혼합 분산: {final_sigma2_mixture:.4f}")
        print(f"최종 목적 함수 값: {best_obj_val:.4f}")
        return optimal_p, optimal_w_V, optimal_w_T
    else:
        print("\n유효한 해를 찾지 못했습니다.")
        return None, None, None

# main.py에서 데이터를 받아와 최적화 작동
if __name__ == "__main__":
    # 실제 main.py에서 15개 태스크의 index_z 데이터를 받아오는 부분
    # 이 부분은 실제 데이터 로딩 로직으로 대체되어야 합니다.
    # 예시: 'data_loader_module.load_episode_data()' 또는 'pd.read_csv(...)' 등
    
    # 여기서는 가상의 실제 에피소드 데이터를 생성하여 사용합니다.
    # 실제 데이터는 np.array 또는 list 형태의 index_z 값들의 집합이어야 합니다.
    # 예시: 15개 태스크에서 수집된 index_z 값들 (각 태스크마다 여러 샘플이 있을 수 있음)
    
    # 실제 데이터 로딩 예시 (가상의 데이터)
    # 예를 들어, 각 태스크의 'impact_z' 또는 'button_displacement' 값이 저장된 리스트라고 가정
    # 이 데이터는 사용자가 버튼을 누른 '깊이'를 나타내며, 시각적 단서의 분포를 형성합니다.
    actual_episode_data = np.array([
        0.05, 0.06, 0.055, 0.062, 0.058, # Task 1
        0.07, 0.075, 0.068, 0.072, 0.071, # Task 2
        0.06, 0.065, 0.059, 0.063, 0.061, # Task 3
        0.08, 0.082, 0.079, 0.081, 0.083, # Task 4
        0.05, 0.053, 0.048, 0.051, 0.052, # Task 5
        0.065, 0.067, 0.064, 0.066, 0.068, # Task 6
        0.07, 0.073, 0.071, 0.074, 0.072, # Task 7
        0.055, 0.057, 0.054, 0.056, 0.058, # Task 8
        0.06, 0.062, 0.059, 0.061, 0.063, # Task 9
        0.075, 0.077, 0.074, 0.076, 0.078, # Task 10
        0.06, 0.063, 0.058, 0.061, 0.062, # Task 11
        0.08, 0.083, 0.078, 0.081, 0.082, # Task 12
        0.05, 0.052, 0.049, 0.051, 0.053, # Task 13
        0.065, 0.068, 0.063, 0.066, 0.067, # Task 14
        0.07, 0.072, 0.069, 0.071, 0.073  # Task 15
    ])
    
    # 혼합 분포의 목표 평균 정의
    # 이 값은 시스템 설계자 또는 사용자의 특정 목표에 따라 결정되어야 하는 중요한 매개변수입니다.
    # 예를 들어, 현재 시각적 평균보다 약간 높은 값을 목표로 설정할 수 있습니다.
    # 사용자의 지각적 목표에 따라 이 값을 조정하세요.
    target_mean_for_mixture = np.mean(actual_episode_data) + 0.005 # 예시: 현재 시각적 평균보다 약간 높은 목표

    # 최적화 실행
    updated_impact_position, updated_w_V, updated_w_T = run_adaptive_impact_position_optimizer(
        episode_data=actual_episode_data,
        mu_target=target_mean_for_mixture,
        alpha=1.0, # 평균 목표 근접성에 대한 가중치 (조정 가능)
        beta=1.0   # 분산 최소화에 대한 가중치 (조정 가능)
    )

    if updated_impact_position is not None:
        print(f"\n--- 최적화 결과 ---")
        print(f"다음 반복 또는 에피소드에 권장되는 새로운 impact_position: {updated_impact_position:.4f}")
        print(f"권장되는 시각적 단서 가중치 (w_V): {updated_w_V:.4f}")
        print(f"권장되는 진동 촉각 단서 가중치 (w_T): {updated_w_T:.4f}")
        
        # 이 updated_impact_position 값을 실제 시스템에 적용하는 로직 추가
        # 예: system_config.set_impact_position(updated_impact_position)
        # 또는 다음 에피소드 시작 시 이 값을 사용