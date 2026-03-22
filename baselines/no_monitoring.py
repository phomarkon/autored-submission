"""Baseline: No monitoring — always accept untrusted code."""


def run_protocol(problem, untrusted_solution, trusted_model, untrusted_model):
    return "ACCEPT", {"baseline": "no_monitoring"}
