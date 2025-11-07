diff --git a/src/rl_transformer/model.py b/src/rl_transformer/model.py
new file mode 100644
index 0000000000000000000000000000000000000000..849dbf89e445259cfd7c794d73d3a89d98273c70
--- /dev/null
+++ b/src/rl_transformer/model.py
@@ -0,0 +1,57 @@
+"""Transformer-based policy/value model for constrained optimization."""
+from __future__ import annotations
+
+from typing import Tuple
+
+import torch
+from torch import nn
+
+
+class TransformerPolicy(nn.Module):
+    """Transformer that maps state histories to action distributions."""
+
+    def __init__(
+        self,
+        state_dim: int,
+        action_dim: int,
+        d_model: int,
+        nhead: int,
+        num_encoder_layers: int,
+        num_decoder_layers: int,
+        dim_feedforward: int,
+        dropout: float,
+    ) -> None:
+        super().__init__()
+        self.state_projection = nn.Linear(state_dim, d_model)
+        self.action_projection = nn.Linear(action_dim, d_model)
+        self.positional_encoding = nn.Parameter(torch.zeros(1, 512, d_model))
+        self.transformer = nn.Transformer(
+            d_model=d_model,
+            nhead=nhead,
+            num_encoder_layers=num_encoder_layers,
+            num_decoder_layers=num_decoder_layers,
+            dim_feedforward=dim_feedforward,
+            dropout=dropout,
+            batch_first=True,
+        )
+        self.policy_head = nn.Linear(d_model, action_dim)
+        self.value_head = nn.Linear(d_model, 1)
+        self.log_std = nn.Parameter(torch.zeros(action_dim))
+
+    def forward(self, states: torch.Tensor, actions: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
+        """Forward pass returning per-step action means and value estimates."""
+
+        state_tokens = self.state_projection(states)
+        action_tokens = self.action_projection(actions)
+        seq_len = state_tokens.size(1)
+        positional = self.positional_encoding[:, :seq_len]
+        state_tokens = state_tokens + positional
+        action_tokens = action_tokens + positional
+        memory = self.transformer.encoder(state_tokens)
+        decoded = self.transformer.decoder(action_tokens, memory)
+        policy_means = self.policy_head(decoded)
+        values = self.value_head(memory).squeeze(-1)
+        return policy_means, values
+
+
+__all__ = ["TransformerPolicy"]
