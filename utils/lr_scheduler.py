import math
from typing import List
import torch


class WarmupPolyLR(torch.optim.lr_scheduler._LRScheduler):
    def __init__(self,
                 optimizer: torch.optim.Optimizer,
                 max_iters: int,
                 warmup_factor: float = 0.001,
                 warmup_iters: int = 1000,
                 warmup_method: str = "linear",
                 last_epoch: int = -1,
                 power: float = 0.9,
                 constant_ending: float = 0.0):
        self.max_iters = max_iters
        self.warmup_factor = warmup_factor
        self.warmup_iters = warmup_iters
        self.warmup_method = warmup_method
        self.power = power
        self.constant_ending = constant_ending
        super().__init__(optimizer, last_epoch)

    def get_lr(self) -> List[float]:
        warmup_factor = self._get_warmup_factor_at_iter(self.warmup_method, self.last_epoch,
                                                        self.warmup_iters, self.warmup_factor)
        if self.constant_ending > 0 and warmup_factor == 1.0:
            # Constant ending lr.
            if math.pow((1.0 - self.last_epoch / self.max_iters), self.power) < self.constant_ending:
                return [base_lr * self.constant_ending for base_lr in self.base_lrs]
        return [base_lr * warmup_factor * math.pow((1.0 - self.last_epoch / self.max_iters), self.power)
                for base_lr in self.base_lrs]

    def _compute_values(self) -> List[float]:
        # The new interface
        return self.get_lr()

    def _get_warmup_factor_at_iter(self, method: str, iter: int, warmup_iters: int, warmup_factor: float) -> float:
        """
        Return the learning rate warmup factor at a specific iteration.
        See :paper:`ImageNet in 1h` for more details.
        Args:
            method (str): warmup method; either "constant" or "linear".
            iter (int): iteration at which to calculate the warmup factor.
            warmup_iters (int): the number of warmup iterations.
            warmup_factor (float): the base warmup factor (the meaning changes according
                to the method used).
        Returns:
            float: the effective warmup factor at the given iteration.
        """
        if iter >= warmup_iters:
            return 1.0

        if method == "constant":
            return warmup_factor
        elif method == "linear":
            alpha = iter / warmup_iters
            return warmup_factor * (1 - alpha) + alpha
        else:
            raise ValueError("Unknown warmup method: {}".format(method))
