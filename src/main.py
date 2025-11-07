diff --git a/src/main.py b/src/main.py
new file mode 100644
index 0000000000000000000000000000000000000000..34b0d5ba787d362328da9fbbb38dd66bd6c40ccb
--- /dev/null
+++ b/src/main.py
@@ -0,0 +1,57 @@
+"""Entry point for running RL-transformer optimization experiments."""
+from __future__ import annotations
+
+import argparse
+from pathlib import Path
+
+from rl_transformer.config import load_config
+from rl_transformer.environment import OptimizationEnvironment
+from rl_transformer.trainer import Trainer
+
+
+def build_environment(config) -> OptimizationEnvironment:
+    env_cfg = config.environment
+    return OptimizationEnvironment(
+        state_dim=env_cfg.state_dim,
+        action_dim=env_cfg.action_dim,
+        constraint_dim=env_cfg.constraint_dim,
+        horizon=env_cfg.horizon,
+    )
+
+
+def parse_args() -> argparse.Namespace:
+    parser = argparse.ArgumentParser(description=__doc__)
+    parser.add_argument(
+        "--config",
+        type=Path,
+        default=Path("configs/default.yaml"),
+        help="Path to the YAML configuration file.",
+    )
+    parser.add_argument(
+        "--device",
+        type=str,
+        default="cpu",
+        help="Compute device to use (e.g., 'cpu' or 'cuda').",
+    )
+    return parser.parse_args()
+
+
+def main() -> None:
+    args = parse_args()
+    config = load_config(args.config)
+    trainer = Trainer(config=config, environment_factory=build_environment, device=args.device)
+    final_state = trainer.run()
+    print(
+        "Training finished",
+        {
+            "steps": final_state.step,
+            "episodes": final_state.episodes,
+            "avg_reward": final_state.total_reward / max(1, final_state.step),
+            "avg_penalty": final_state.total_penalty / max(1, final_state.step),
+            "avg_return_per_episode": final_state.total_reward / max(1, final_state.episodes),
+        },
+    )
+
+
+if __name__ == "__main__":
+    main()
