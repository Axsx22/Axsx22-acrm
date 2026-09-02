"""
Statistical Significance — Refactored v2.0
Contract: uses Welch's t-test and bootstrap CI.
"""

import math
import random
from typing import List, Tuple, Dict


class StatisticalSignificanceTester:
    """
    Statistical testing for benchmark comparison.

    Invariant: bootstrap uses sampling WITH replacement.
    """

    def bootstrap_mean(self, data: List[float], n_resamples: int = 1000) -> List[float]:
        n = len(data)
        return [sum(random.choices(data, k=n)) / n 
                for _ in range(n_resamples)]

    def bootstrap_ci(self, data: List[float], alpha: float = 0.05) -> Tuple[float, float]:
        means = sorted(self.bootstrap_mean(data))
        lower_idx = int((alpha / 2) * len(means))
        upper_idx = int((1 - alpha / 2) * len(means))
        return means[lower_idx], means[upper_idx]

    def t_test_independent(self, x: List[float], y: List[float]) -> Dict[str, float]:
        """Welch's t-test for unequal variances."""
        def mean(a):
            return sum(a) / len(a)

        def var(a):
            m = mean(a)
            return sum((i - m) ** 2 for i in a) / (len(a) - 1)

        mx, my = mean(x), mean(y)
        vx, vy = var(x), var(y)
        nx, ny = len(x), len(y)

        t_den = math.sqrt(vx / nx + vy / ny)
        if t_den == 0:
            return {"t_stat": 0.0, "df": 0}

        t_stat = (mx - my) / t_den
        df_num = (vx / nx + vy / ny) ** 2
        df_den = (vx ** 2) / (nx ** 2 * (nx - 1)) + (vy ** 2) / (ny ** 2 * (ny - 1))

        return {
            "t_stat": round(t_stat, 4),
            "df": round(df_num / max(df_den, 1e-9), 2)
        }

    def compare_metrics(self, acrm_values: List[float], 
                        baseline_values: List[float]) -> Dict:
        return {
            "acrm_ci": self.bootstrap_ci(acrm_values),
            "baseline_ci": self.bootstrap_ci(baseline_values),
            "t_test": self.t_test_independent(acrm_values, baseline_values)
        }
