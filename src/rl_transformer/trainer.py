diff --git a/src/rl_transformer/trainer.py b/src/rl_transformer/trainer.py
new file mode 100644
index 0000000000000000000000000000000000000000..f90b6655b454810ee8be2efdac61d9777d0315b3
--- /dev/null
+++ b/src/rl_transformer/trainer.py
@@ -0,0 +1,168 @@
+"""Training loop scaffolding for RL-transformer optimization."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from typing import Callable, Sequence
+
+import torch
+from torch import nn, optim
+from torch.distributions import Normal
+from tqdm import tqdm
+
+from .config import ExperimentConfig
+from .environment import OptimizationEnvironment
+from .model import TransformerPolicy
+
+
+@dataclass
+class TrainingState:
+    """Keeps track of metrics during training."""
+
+    step: int = 0
+    total_reward: float = 0.0
+    total_penalty: float = 0.0
+    episodes: int = 0
+
+
+class Trainer:
+    """Simple trainer integrating the environment and transformer policy."""
+
+    def __init__(
+        self,
+        config: ExperimentConfig,
+        environment_factory: Callable[[ExperimentConfig], OptimizationEnvironment],
+        device: torch.device | str = "cpu",
+    ) -> None:
+        self.config = config
+        self.device = torch.device(device)
+        self.environment = environment_factory(config)
+        self.model = TransformerPolicy(
+            state_dim=self.environment.state_dim,
+            action_dim=self.environment.action_dim,
+            d_model=config.model.d_model,
+            nhead=config.model.nhead,
+            num_encoder_layers=config.model.num_encoder_layers,
+            num_decoder_layers=config.model.num_decoder_layers,
+            dim_feedforward=config.model.dim_feedforward,
+            dropout=config.model.dropout,
+        ).to(self.device)
+        self.optimizer = optim.Adam(self.model.parameters(), lr=config.training.learning_rate)
+        self.gamma = config.training.gamma
+        self.grad_clip_norm = config.training.grad_clip_norm
+        self.value_coef = config.training.value_coef
+        self.entropy_coef = config.training.entropy_coef
+
+    def run(self) -> TrainingState:
+        """Run the training loop for the configured number of steps."""
+
+        state = self.environment.reset()
+        training_state = TrainingState()
+        self.model.train()
+        state_history: list[torch.Tensor] = []
+        prev_action_history: list[torch.Tensor] = []
+        reward_history: list[torch.Tensor] = []
+        log_prob_history: list[torch.Tensor] = []
+        value_history: list[torch.Tensor] = []
+        entropy_history: list[torch.Tensor] = []
+
+        def reset_episode_buffers() -> None:
+            state_history.clear()
+            prev_action_history.clear()
+            reward_history.clear()
+            log_prob_history.clear()
+            value_history.clear()
+            entropy_history.clear()
+
+        last_action = torch.zeros(self.environment.action_dim, dtype=torch.float32, device=self.device)
+
+        progress = tqdm(range(self.config.training.total_steps), desc="Training")
+        for step in progress:
+            training_state.step = step + 1
+            state_tensor = torch.tensor(state, dtype=torch.float32, device=self.device)
+
+            state_history.append(state_tensor)
+            prev_action_history.append(last_action)
+
+            states_seq = torch.stack(state_history).unsqueeze(0)
+            prev_actions_seq = torch.stack(prev_action_history).unsqueeze(0)
+
+            policy_means, values = self.model(states_seq, prev_actions_seq)
+            action_mean = policy_means[:, -1]
+            value = values[:, -1]
+            std = self.model.log_std.exp().clamp(min=1e-3, max=10.0).unsqueeze(0).expand_as(action_mean)
+            dist = Normal(action_mean, std)
+            action = dist.rsample()
+            log_prob = dist.log_prob(action).sum(-1)
+            entropy = dist.entropy().sum(-1)
+
+            env_action = action.squeeze(0).detach().cpu().numpy()
+            transition = self.environment.step(env_action)
+            training_state.total_reward += float(transition.reward)
+            training_state.total_penalty += float(transition.info.get("penalty", 0.0))
+
+            reward_history.append(torch.tensor(transition.reward, dtype=torch.float32, device=self.device))
+            log_prob_history.append(log_prob.squeeze(0))
+            value_history.append(value.squeeze(0))
+            entropy_history.append(entropy.squeeze(0))
+
+            if transition.done:
+                self._optimize(reward_history, log_prob_history, value_history, entropy_history)
+                training_state.episodes += 1
+                reset_episode_buffers()
+                state = self.environment.reset()
+                last_action = torch.zeros_like(last_action)
+            else:
+                state = transition.next_state
+                last_action = action.squeeze(0).detach()
+
+            progress.set_postfix(
+                reward=training_state.total_reward / training_state.step,
+                penalty=training_state.total_penalty / training_state.step,
+                episodes=training_state.episodes,
+            )
+
+        if reward_history:
+            self._optimize(reward_history, log_prob_history, value_history, entropy_history)
+            reset_episode_buffers()
+
+        return training_state
+
+    def _optimize(
+        self,
+        rewards: Sequence[torch.Tensor],
+        log_probs: Sequence[torch.Tensor],
+        values: Sequence[torch.Tensor],
+        entropies: Sequence[torch.Tensor],
+    ) -> None:
+        """Backpropagate through the collected trajectory."""
+
+        if not rewards:
+            return
+
+        rewards_tensor = torch.stack(list(rewards)).to(self.device)
+        log_probs_tensor = torch.stack(list(log_probs)).to(self.device)
+        values_tensor = torch.stack(list(values)).to(self.device)
+        entropies_tensor = torch.stack(list(entropies)).to(self.device)
+
+        returns = torch.zeros_like(rewards_tensor)
+        future_return = torch.zeros(1, device=self.device)
+        for t in reversed(range(len(rewards_tensor))):
+            future_return = rewards_tensor[t] + self.gamma * future_return
+            returns[t] = future_return
+
+        advantages = returns - values_tensor.detach()
+        advantages = (advantages - advantages.mean()) / (advantages.std(unbiased=False) + 1e-8)
+
+        policy_loss = -(advantages * log_probs_tensor).mean()
+        value_loss = nn.functional.mse_loss(values_tensor, returns)
+        entropy_term = entropies_tensor.mean()
+
+        loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy_term
+
+        self.optimizer.zero_grad()
+        loss.backward()
+        nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
+        self.optimizer.step()
+
+
+__all__ = ["Trainer", "TrainingState"]
