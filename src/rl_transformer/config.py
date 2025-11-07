diff --git a/src/rl_transformer/config.py b/src/rl_transformer/config.py
new file mode 100644
index 0000000000000000000000000000000000000000..d6c5b11b892bc8b47a4728de89ca550e46f5dde3
--- /dev/null
+++ b/src/rl_transformer/config.py
@@ -0,0 +1,73 @@
+"""Configuration utilities for RL-transformer optimization experiments."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Any, Dict
+
+import yaml
+
+
+@dataclass
+class EnvironmentConfig:
+    """Configuration describing the optimization environment."""
+
+    name: str
+    state_dim: int
+    action_dim: int
+    constraint_dim: int
+    horizon: int
+
+
+@dataclass
+class ModelConfig:
+    """Configuration for the transformer policy/value model."""
+
+    d_model: int
+    nhead: int
+    num_encoder_layers: int
+    num_decoder_layers: int
+    dim_feedforward: int
+    dropout: float
+
+
+@dataclass
+class TrainingConfig:
+    """High-level optimization/training configuration."""
+
+    total_steps: int
+    batch_size: int
+    gamma: float
+    learning_rate: float
+    grad_clip_norm: float
+    value_coef: float
+    entropy_coef: float
+
+
+@dataclass
+class ExperimentConfig:
+    """Aggregate configuration loaded from YAML files."""
+
+    environment: EnvironmentConfig
+    model: ModelConfig
+    training: TrainingConfig
+
+    @classmethod
+    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentConfig":
+        return cls(
+            environment=EnvironmentConfig(**data["environment"]),
+            model=ModelConfig(**data["model"]),
+            training=TrainingConfig(**data["training"]),
+        )
+
+    @classmethod
+    def load(cls, path: str | Path) -> "ExperimentConfig":
+        with Path(path).open("r", encoding="utf-8") as fp:
+            raw = yaml.safe_load(fp)
+        return cls.from_dict(raw)
+
+
+def load_config(path: str | Path) -> ExperimentConfig:
+    """Convenience wrapper for loading experiment configuration files."""
+
+    return ExperimentConfig.load(path)
