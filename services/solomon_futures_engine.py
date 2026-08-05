import sqlite3
from contextlib import closing
import dataclasses
import hashlib
import math
import time
from typing import Any, Dict, List, Optional, Tuple, Protocol

route_key = "solomon_futures_engine"

# ==============================================================================
# PHASE 2: CONTRACTS & POLICY
# ==============================================================================

@dataclasses.dataclass(frozen=True)
class Candidate:
    candidate_id: str
    event_id: str
    domain: str
    source_name: str
    source_record_id: str
    source_mode: str  # TEST|SIMULATION|SHADOW|LIVE
    source_timestamp: str
    ingested_at: str
    pre_simulation_confidence: float
    data_quality_score: float
    features: Dict[str, Any]

    def validate(self) -> List[str]:
        errors = []
        if self.source_mode not in ["TEST", "SIMULATION", "SHADOW", "LIVE"]:
            errors.append("INVALID_SOURCE_MODE")
        if self.pre_simulation_confidence < 0.0 or self.pre_simulation_confidence > 100.0:
            errors.append("OUT_OF_RANGE_CONFIDENCE")
        return errors

@dataclasses.dataclass
class SimulationConfig:
    pre_simulation_confidence_min: float = 90.0
    simulated_probability_min: float = 0.90
    confidence_level: float = 0.95
    confidence_interval_lower_bound_min: float = 0.90
    minimum_trials: int = 1000
    minimum_data_quality: float = 90.0
    sensitivity_floor: float = 0.88

@dataclasses.dataclass
class QualificationResult:
    pre_simulation_qualified: bool
    reasons: List[str]

@dataclasses.dataclass
class SimulationResult:
    run_id: str
    candidate_id: str
    status: str
    source_mode: str
    qualification: QualificationResult
    simulation: Dict[str, Any]
    audit: Dict[str, Any]
    created_at: str

class WilsonInterval:
    @staticmethod
    def calculate(successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float]:
        if trials == 0:
            return 0.0, 0.0
        # Z-score for 95% confidence is approx 1.96
        z = 1.96
        p = successes / trials

        denominator = 1 + z**2 / trials
        center = p + z**2 / (2 * trials)
        spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * trials)) / trials)

        lower = (center - spread) / denominator
        upper = (center + spread) / denominator
        return max(0.0, lower), min(1.0, upper)

# ==============================================================================
# PHASE 3: SIMULATION ADAPTER
# ==============================================================================

class SimulationAdapter(Protocol):
    name: str
    version: str
    def build_scenario(self, candidate: Candidate) -> Dict[str, Any]: ...
    def simulate_trial(self, scenario: Dict[str, Any], rng_seed: int) -> bool: ...
    def sensitivity_variants(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]: ...

class UniversalFuturesAdapter:
    name = "universal_omni"
    version = "2.0.0"

    def build_scenario(self, candidate: Candidate) -> Dict[str, Any]:
        """Extracts multidimensional global metrics from the candidate features."""
        # Baseline probability of the event occurring (e.g. historical average)
        base = candidate.features.get("base_prob", 0.5)
        # Market/Domain volatility (0.0 to 1.0) - how wildly things swing
        volatility = candidate.features.get("volatility_index", 0.1)
        # Structural support (0.0 to 1.0) - resistance to crashing
        support = candidate.features.get("historical_support", 0.5)
        # Chaos multiplier (0.0 to 1.0) - unexpected external shocks (geopolitical, weather)
        chaos_risk = candidate.features.get("geopolitical_risk", 0.05)
        
        return {
            "base_prob": base,
            "volatility": volatility,
            "support": support,
            "chaos_risk": chaos_risk
        }

    def simulate_trial(self, scenario: Dict[str, Any], rng_seed: int) -> bool:
        """
        Multi-Dimensional Monte Carlo Step.
        Calculates a highly complex probabilistic outcome rather than a simple coin flip.
        """
        # We use a deterministic hash chain to simulate multiple random variables from one seed
        h1 = int(hashlib.md5(f"{rng_seed}_A".encode()).hexdigest(), 16) % 10000 / 10000.0
        h2 = int(hashlib.md5(f"{rng_seed}_B".encode()).hexdigest(), 16) % 10000 / 10000.0
        h3 = int(hashlib.md5(f"{rng_seed}_C".encode()).hexdigest(), 16) % 10000 / 10000.0

        # Base event roll
        event_roll = h1
        
        # Volatility swing (can push the roll up or down)
        swing = (h2 - 0.5) * scenario["volatility"]
        
        # Chaos injection (fat-tail risk)
        if h3 < scenario["chaos_risk"]:
            # A black swan event occurred in this simulation trial, heavily shifting the outcome
            swing -= 0.4
            
        # Support buffer (mitigates negative swings)
        if swing < 0:
            swing *= (1.0 - scenario["support"])
            
        final_outcome_value = event_roll + swing
        
        # If the final calculated value is below the base probability threshold, the event "fails" to trigger/win
        return final_outcome_value < scenario["base_prob"]

    def sensitivity_variants(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Stress-tests the scenario by increasing chaos and volatility."""
        return [
            {
                "base_prob": scenario["base_prob"],
                "volatility": min(1.0, scenario["volatility"] * 1.5), # 50% spike in volatility
                "support": max(0.0, scenario["support"] * 0.8),       # 20% drop in support
                "chaos_risk": min(1.0, scenario["chaos_risk"] * 2.0)  # 2x black swan risk
            }
        ]

class FuturesEngine:
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.adapters = {"universal_omni": UniversalFuturesAdapter()}

    def _evaluate_gate_a(self, candidate: Candidate) -> QualificationResult:
        errors = candidate.validate()
        if errors:
            return QualificationResult(False, errors)

        reasons = []
        if candidate.pre_simulation_confidence >= self.config.pre_simulation_confidence_min:
            reasons.append("PRE_SIMULATION_CONFIDENCE_AT_LEAST_90")
        else:
            return QualificationResult(False, ["PRE_SIMULATION_SCORE_BELOW_90"])

        if candidate.data_quality_score >= self.config.minimum_data_quality:
            reasons.append("DATA_QUALITY_PASSED")
        else:
            return QualificationResult(False, ["DATA_QUALITY_TOO_LOW"])

        return QualificationResult(True, reasons)

    def process_candidate(self, candidate: Candidate, adapter_name: str = "universal_omni", run_id: str = "auto", seed: int = 42) -> SimulationResult:
        qual = self._evaluate_gate_a(candidate)

        if not qual.pre_simulation_qualified:
            return SimulationResult(
                run_id=run_id,
                candidate_id=candidate.candidate_id,
                status="PRE_SIM_NOT_QUALIFIED",
                source_mode=candidate.source_mode,
                qualification=qual,
                simulation={},
                audit={},
                created_at=str(time.time())
            )

        adapter = self.adapters.get(adapter_name)
        if not adapter:
            raise ValueError(f"ADAPTER_NOT_FOUND: {adapter_name}")

        scenario = adapter.build_scenario(candidate)

        # Batch simulation
        successes = 0
        for i in range(self.config.minimum_trials):
            if adapter.simulate_trial(scenario, seed + i):
                successes += 1

        prob = successes / self.config.minimum_trials
        lower, upper = WilsonInterval.calculate(successes, self.config.minimum_trials, self.config.confidence_level)

        # Sensitivity
        variants = adapter.sensitivity_variants(scenario)
        min_variant_prob = 1.0
        for v in variants:
            v_succ = 0
            for i in range(self.config.minimum_trials):
                if adapter.simulate_trial(v, seed + i):
                    v_succ += 1
            min_variant_prob = min(min_variant_prob, v_succ / self.config.minimum_trials)

        # Gate B
        status = "CONFIRMED_90_PLUS"
        if prob < self.config.simulated_probability_min:
            status = "NOT_CONFIRMED_90_PLUS"
        elif lower < self.config.confidence_interval_lower_bound_min:
            status = "NOT_CONFIRMED_90_PLUS"
        elif min_variant_prob < self.config.sensitivity_floor:
            status = "SENSITIVITY_FLOOR_FAILED"

        return SimulationResult(
            run_id=run_id,
            candidate_id=candidate.candidate_id,
            status=status,
            source_mode=candidate.source_mode,
            qualification=qual,
            simulation={
                "adapter": adapter.name,
                "trials": self.config.minimum_trials,
                "successes": successes,
                "simulation_probability": prob,
                "interval_lower": lower,
                "interval_upper": upper,
                "sensitivity_floor": min_variant_prob
            },
            audit={},
            created_at=str(time.time())
        )

# ==============================================================================
# PHASE 4: PERSISTENCE & IDEMPOTENCY
# ==============================================================================

class FuturesRepository:
    def __init__(self, db_path="solomon_soss.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                # Use canonical WAL journal mode
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS futures_simulation_runs (
                        run_id TEXT PRIMARY KEY,
                        candidate_id TEXT,
                        status TEXT,
                        source_mode TEXT,
                        simulation_probability REAL,
                        interval_lower REAL,
                        interval_upper REAL,
                        created_at TEXT
                    )
                """)

    def check_idempotency(self, candidate_id: str, source_mode: str) -> bool:
        """Prevent same candidate/mode execution logic."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 1 FROM futures_simulation_runs
                WHERE candidate_id = ? AND source_mode = ?
                AND status IN ('CONFIRMED_90_PLUS', 'NOT_CONFIRMED_90_PLUS', 'SENSITIVITY_FLOOR_FAILED')
            """, (candidate_id, source_mode))
            return cur.fetchone() is not None

    def save_run(self, result: SimulationResult):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                sim = result.simulation
                conn.execute("""
                    INSERT OR IGNORE INTO futures_simulation_runs
                    (run_id, candidate_id, status, source_mode, simulation_probability, interval_lower, interval_upper, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f'{result.run_id}_{result.candidate_id}', result.candidate_id, result.status, result.source_mode,
                    sim.get("simulation_probability", 0.0), sim.get("interval_lower", 0.0),
                    sim.get("interval_upper", 0.0), result.created_at
                ))
