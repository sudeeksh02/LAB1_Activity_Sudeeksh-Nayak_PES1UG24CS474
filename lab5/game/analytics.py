import math
from typing import List, Dict, Any
from .round import RoundResult

class ReflexAnalytics:
    """Statistical analytics engine for cognitive reaction telemetry."""

    @staticmethod
    def compute_session_stats(rounds: List[RoundResult]) -> Dict[str, Any]:
        valid_latencies = [r.latency_ms for r in rounds if r.latency_ms > 0 and not r.is_false_start and r.is_correct_go]
        false_starts = sum(1 for r in rounds if r.is_false_start)
        timeouts = sum(1 for r in rounds if r.is_timeout)
        total_trials = len(rounds)

        if not valid_latencies:
            return {
                "total_trials": total_trials,
                "valid_trials": 0,
                "average_ms": 0.0,
                "median_ms": 0.0,
                "best_ms": 0,
                "worst_ms": 0,
                "std_dev_ms": 0.0,
                "consistency_score": 0.0,
                "false_starts": false_starts,
                "timeouts": timeouts,
                "rating": "Insufficient Data"
            }

        avg_latency = sum(valid_latencies) / len(valid_latencies)
        sorted_latencies = sorted(valid_latencies)
        n = len(sorted_latencies)
        median_latency = (sorted_latencies[n // 2] if n % 2 != 0 
                          else (sorted_latencies[n // 2 - 1] + sorted_latencies[n // 2]) / 2.0)
        best_latency = sorted_latencies[0]
        worst_latency = sorted_latencies[-1]

        variance = sum((x - avg_latency) ** 2 for x in valid_latencies) / len(valid_latencies)
        std_dev = math.sqrt(variance)

        # Consistency score: 100 - (CV * 100) where CV = std_dev / avg
        cv = std_dev / avg_latency if avg_latency > 0 else 1.0
        consistency = max(0.0, min(100.0, (1.0 - cv) * 100.0))

        # Skill rating tiers based on cognitive research norms
        if avg_latency < 210 and false_starts == 0:
            rating = "Lightning Esports Reflexes (Top 1%)"
        elif avg_latency < 250:
            rating = "Superior Athletic Reflexes (Top 10%)"
        elif avg_latency < 300:
            rating = "Above Average Cognitive Processing"
        elif avg_latency < 380:
            rating = "Normal Human Baseline"
        else:
            rating = "Delayed Reflexes (Practice Recommended)"

        return {
            "total_trials": total_trials,
            "valid_trials": len(valid_latencies),
            "average_ms": round(avg_latency, 1),
            "median_ms": round(median_latency, 1),
            "best_ms": best_latency,
            "worst_ms": worst_latency,
            "std_dev_ms": round(std_dev, 1),
            "consistency_score": round(consistency, 1),
            "false_starts": false_starts,
            "timeouts": timeouts,
            "rating": rating
        }
