import numpy as np
from sympy import symbols, solve

def calculate_equilibrium():
    # 1. 각 주유소의 수요함수 계수 정의
    # q₁ = 100 + 100(p₂ - p₁)
    # q₂ = 500 + 100(p₁ + p₃ - 2p₂)
    # q₃ = 400 - 100(p₃ - p₂)
    
    # 가격을 심볼로 정의
    p1, p2, p3 = symbols('p1 p2 p3')
    
    # 한계비용
    mc1, mc2, mc3 = 0.5, 0.3, 0.7
    
    # 2. 이윤함수의 일계조건
    eq1 = 100 + 100*p2 - 200*p1 + 50  # ∂π₁/∂p₁ = 0
    eq2 = 500 + 100*p1 + 100*p3 - 400*p2 + 60  # ∂π₂/∂p₂ = 0
    eq3 = 400 - 200*p3 + 100*p2 + 70  # ∂π₃/∂p₃ = 0
    
    # 균형 가격 계산
    solution = solve((eq1, eq2, eq3), (p1, p2, p3))
    p1_eq, p2_eq, p3_eq = float(solution[p1]), float(solution[p2]), float(solution[p3])
    
    # 3. 균형 수량 계산
    q1_eq = 100 + 100*(p2_eq - p1_eq)
    q2_eq = 500 + 100*(p1_eq + p3_eq - 2*p2_eq)
    q3_eq = 400 - 100*(p3_eq - p2_eq)
    
    # 4. 이윤 계산
    profit1 = (p1_eq - mc1) * q1_eq
    profit2 = (p2_eq - mc2) * q2_eq
    profit3 = (p3_eq - mc3) * q3_eq
    
    return p1_eq, p2_eq, p3_eq, q1_eq, q2_eq, q3_eq, profit1, profit2, profit3

def calculate_elasticities(p1, p2, p3, q1, q2, q3):
    # 탄력성 행렬 계산
    elasticity_matrix = np.zeros((3, 3))
    
    # 자기가격 탄력성
    elasticity_matrix[0,0] = -100 * (p1/q1)  # 주유소 1
    elasticity_matrix[1,1] = -200 * (p2/q2)  # 주유소 2
    elasticity_matrix[2,2] = -100 * (p3/q3)  # 주유소 3
    
    # 교차가격 탄력성
    elasticity_matrix[0,1] = 100 * (p2/q1)   # 주유소 1에 대한 주유소 2의 영향
    elasticity_matrix[1,0] = 100 * (p1/q2)   # 주유소 2에 대한 주유소 1의 영향
    elasticity_matrix[1,2] = 100 * (p3/q2)   # 주유소 2에 대한 주유소 3의 영향
    elasticity_matrix[2,1] = 100 * (p2/q3)   # 주유소 3에 대한 주유소 2의 영향
    
    return elasticity_matrix

# 결과 계산 및 출력
p1, p2, p3, q1, q2, q3, profit1, profit2, profit3 = calculate_equilibrium()
elasticities = calculate_elasticities(p1, p2, p3, q1, q2, q3)

print("균형 가격:")
print(f"주유소 1: {p1:.2f}")
print(f"주유소 2: {p2:.2f}")
print(f"주유소 3: {p3:.2f}")

print("\n균형 수량:")
print(f"주유소 1: {q1:.0f}")
print(f"주유소 2: {q2:.0f}")
print(f"주유소 3: {q3:.0f}")

print("\n이윤:")
print(f"주유소 1: {profit1:.0f}")
print(f"주유소 2: {profit2:.0f}")
print(f"주유소 3: {profit3:.0f}")

print("\n가격 탄력성 행렬:")
for i in range(3):
    for j in range(3):
        print(f"{elasticities[i,j]:.2f}", end=" ")
    print()
