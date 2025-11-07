diff --git a/src/rl_transformer/environment.py b/src/rl_transformer/environment.py
new file mode 100644
index 0000000000000000000000000000000000000000..78294cca7339de4712072f90d36255cd6a5e610c
--- /dev/null
+++ b/src/rl_transformer/environment.py
@@ -0,0 +1,76 @@
+"""Lightweight optimization environment abstraction."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from typing import Any, Dict
+
+import numpy as np
+
+
+@dataclass
+class Transition:
+    """Container for one environment transition."""
+
+    state: np.ndarray
+    action: np.ndarray
+    reward: float
+    next_state: np.ndarray
+    done: bool
+    info: Dict[str, Any]
+
+
+class OptimizationEnvironment:
+    """Base class that wraps constrained optimization logic as an RL environment."""
+
+    def __init__(self, state_dim: int, action_dim: int, constraint_dim: int, horizon: int) -> None:
+        self.state_dim = state_dim
+        self.action_dim = action_dim
+        self.constraint_dim = constraint_dim
+        self.horizon = horizon
+        self.step_count = 0
+        self._state = np.zeros(self.state_dim, dtype=np.float32)
+
+    def reset(self) -> np.ndarray:
+        """Reset the environment to an initial state."""
+
+        self.step_count = 0
+        self._state = np.zeros(self.state_dim, dtype=np.float32)
+        return self._state.copy()
+
+    def step(self, action: np.ndarray) -> Transition:
+        """Apply an action and advance the environment by one step."""
+
+        self.step_count += 1
+        action = np.clip(action, -1.0, 1.0)
+        current_state = self._state.copy()
+        next_state = np.random.randn(self.state_dim).astype(np.float32)
+        reward = -np.linalg.norm(action)
+        constraints = np.maximum(0.0, np.random.randn(self.constraint_dim))
+        penalty = constraints.sum()
+        done = self.step_count >= self.horizon
+        info: Dict[str, Any] = {
+            "constraints": constraints,
+            "penalty": penalty,
+        }
+        self._state = next_state
+        return Transition(
+            state=current_state,
+            action=action,
+            reward=reward - penalty,
+            next_state=next_state,
+            done=done,
+            info=info,
+        )
+
+    def sample_action(self) -> np.ndarray:
+        """Sample a random action; useful for bootstrapping policies."""
+
+        return np.random.uniform(low=-1.0, high=1.0, size=self.action_dim).astype(np.float32)
+
+    def render(self) -> None:
+        """Optional rendering hook for visualization."""
+
+        print(f"Step {self.step_count}: horizon={self.horizon}")
+
+
+__all__ = ["OptimizationEnvironment", "Transition"]
