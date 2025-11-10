# RL Transformer Optimizer

이 저장소는 Transformer 기반 정책과 강화학습을 결합하여 제약 조건이 있는 최적화 문제를 탐색하기 위한 실험 환경을 제공합니다.

## 구성 요소

- **`pyproject.toml`**: 필요한 파이썬 의존성과 개발 도구(black, ruff)를 정의합니다.
- **`configs/default.yaml`**: 환경, 모델, 학습 하이퍼파라미터를 정의한 기본 실험 설정입니다.
- **`src/rl_transformer/`**: 핵심 파이썬 모듈
  - `config.py`: YAML 설정을 Dataclass로 로드합니다.
  - `environment.py`: 제약 조건이 있는 최적화 환경의 기본 구현입니다.
  - `model.py`: 상태/행동 히스토리를 입력으로 받아 확률적 행동 평균과 가치를 예측하는 Transformer 정책-가치 결합 모델입니다.
  - `trainer.py`: Normal 분포 기반 actor-critic 학습 루프를 수행하고, 엔트로피 정규화를 지원하는 트레이너입니다.
- **`src/main.py`**: 설정 파일을 로드하고 학습을 실행하는 진입점 스크립트입니다.

## 실행 방법

```bash
pip install -e .
python -m src.main --config configs/default.yaml --device cpu
```

기본 환경은 무작위로 생성되는 상태와 제약 페널티를 사용한 단순한 예제입니다. 실제 문제에 맞게 `OptimizationEnvironment` 클래스를 상속하여 환경 로직을 확장할 수 있습니다. `training` 설정에는 `value_coef`와 `entropy_coef`가 포함되어 있어 가치 함수 손실 가중치와 탐색을 위한 엔트로피 보너스를 조정할 수 있습니다.


