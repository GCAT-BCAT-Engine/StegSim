Governance Pipeline and Periodic Transition Table – Status and Roadmap

This document summarises the current state of the governance model implementation and outlines a roadmap for integrating all components into a full, end‑to‑end pipeline.  It is intended as a living reference for developers working on the StegVerse governance framework and demo site.

Current Components

The project has grown from a few standalone validators into a layered architecture that supports deterministic admissibility decisions, cost aggregation, receipt generation and replay, tamper detection, and reversible gating.  The key layers are:
	1.	GCAT/BCAT (Global/Basic Constraint Admissibility Tests) – Validates global invariants (sum of cost fractions equals 1) and checks for negative or missing values.  A candidate is denied if invariants are violated and fail‑closed if input values are missing or non‑numeric.
	2.	ECAT (Entity Constraint Admissibility Transform) – Measures an entity’s fitness to act based on reputation (R), stake (S), history divergence (H), and co‑ownership weights (W).  Costs are normalised by a shared base_cost constant; penalties for low reputation or stake, high history divergence, and co‑owner rejection are aggregated and compared against a budget.  ECAT passes only when each condition is above its minimum threshold and cost does not exceed the budget.
	3.	ICAT (Integrity Constraint Admissibility Transform) – Checks the integrity of proofs, witness attestations, conservation laws, and inverse constraints.  Each component adds a cost term based on required proof/attestation/invariant checks, and a candidate is denied if any proof is invalid, witness quorum is insufficient, conservation fails, or inverses cannot be checked.  Missing or malformed fields result in fail‑closed.
	4.	Probability of Existence (PE) – Determines whether a transition is likely to exist or not, using a probability p with a minimum threshold p_min.  If p is below the threshold, the candidate is denied; if p is missing or not numeric, the result is fail‑closed.  The cost for existence is λ_PE * base_cost * (1 – p), and budgets cap how much penalty can be tolerated.
	5.	Inference Window (IW) – Represents the proportion of available context used by an inference model before making a decision.  A window size w∈[0,1] below the minimum threshold leads to denial; missing or invalid window sizes lead to fail‑closed.  Cost is λ_w * base_cost * (1 – w).  This layer is symmetrical with the temporal‑gap gate; swapping window and gap sizes yields complementary costs, preserving reversibility ￼ ￼.
	6.	Triad – Aggregates GCAT/BCAT, ECAT, ICAT, Probability of Existence, and Inference Window into a single decision.  Costs from each layer are normalised by the same base‑cost constant.  A candidate is fail‑closed if any layer fails closed; denied if any layer denies; otherwise allowed if costs stay within budget.  The Triad supports both the original gcat/bcat separation and a combined gcat_bcat structure.
	7.	Full Pipeline – A wrapper that invokes the Triad and provides placeholders for additional gates (Rigel recoverability, reconstruction confidence, temporal lag, etc.).  It computes aggregated costs and orchestrates the decision logic.  The current implementation stubs out these extra layers, leaving room for future integration.

Implemented Features

Deterministic Validation

All validators are deterministic functions that accept candidate JSON files and return an outcome (ALLOW, DENY, FAIL_CLOSED) together with cost details and reasons.  They support both command‑line invocation and integration into higher‑level pipelines.

Receipts and Replay

For each candidate evaluation, the sandbox adapter produces a receipt containing the candidate ID, outcome, reason, cost summary, and a hash of the input basis.  Receipts are chained via prev_receipt_hash to ensure provenance.  Replay scripts re‑compute outcomes from receipts and confirm that the chain has not been tampered with.  Tamper‑detection tests intentionally alter a receipt and verify that the chain becomes invalid.

Scalar Cost Constant

Each layer computes a cost component by multiplying deviations from ideal behaviour by the same base cost.  This constant ensures that all cost terms have the same dimension and can be aggregated across GCAT/BCAT, ECAT, ICAT, PE, and IW.  In practice, a base cost of 1.0 is used, so the total triad cost equals the sum of each layer’s cost after weighting by its λ parameters.

Periodic Table of Transitions

The project includes a draft “Periodic Table of Transitions” document (see periodic_table_transitions.md) that classifies AI‑system actions into categories (e.g., Identity, Memory, Finance, Physical execution, Inference).  Each category lists typical operations and suggests which governance gates apply.  This taxonomy helps map real AI decisions into the governance framework.

Demo Candidates

Sample candidate files have been created for:
	•	T00 – Read Identity: a harmless read operation that passes all layers.
	•	T11 – Generate Memory: a memory update requiring entity fitness and valid proofs.
	•	Additional categories can be added by placing files into full_pipeline/demo_periodic_candidates.

Outstanding Tasks and Roadmap
	1.	Extend Remaining Gates – The full pipeline currently stubs out Rigel (recoverability), reconstruction confidence, and temporal‑lag.  These must be fully implemented.  Each should compute its own cost term, apply a minimum threshold, and contribute to the aggregated cost and final outcome.
	2.	Update Orchestrator – The high‑level orchestrator (stegverse_math_solver_orchestrator_v1.yml) must call the new full_pipeline_validator and handle the additional gates.  Once Rigel, reconstruction, and temporal‑lag validators are written, modify the YAML to add their invocation and merge their results.
	3.	Expand Periodic Candidates – The periodic table should be expanded to cover all defined categories (e.g., T21 Transfer Finance, T50 Execute Physical, T71 Compose Inference).  For each, create representative candidate JSON files exercising edge cases (boundary values, budget exceedance, missing fields, adversarial inputs).
	4.	Integrate Demo Site – The demo site should use the full pipeline to evaluate AI actions in real time.  This involves exposing an API or internal call that submits a candidate JSON to the validator, returns an outcome and cost breakdown, and stores the receipt chain for audit.  UI elements can display whether an action is allowed, denied, or fails closed, along with reasoning.
	5.	Entropy and Reversibility Tests – To confirm that inference‑window and gap gates are symmetrical, develop paired test cases that swap window and gap sizes.  The total cost should remain constant, and reversing a decision should not introduce additional entropy.  These tests can be automated in the sandbox.
	6.	Documentation and Specs – Finalise specifications for each layer (especially the new ones) and publish them in the docs/ directory.  Ensure that the Periodic Table is clearly referenced and maps to candidate file names.  Continue to maintain this README as development progresses.

How to Run the Full Pipeline
	1.	Ensure that Python dependencies are installed (see requirements.txt).
	2.	Place your candidate JSON files in a directory, such as full_pipeline/demo_periodic_candidates.
	3.	Run the full pipeline validator:

python full_pipeline/full_pipeline_validator.py --vectors full_pipeline/demo_periodic_candidates

This produces a full_pipeline_report.json and a Markdown summary in full_pipeline/brain_reports/.

	4.	To generate receipts and verify the chain, use the sandbox adapter (if available) as follows:

python full_pipeline/sandbox_adapter.py --vectors full_pipeline/demo_periodic_candidates
python full_pipeline/receipt_replay.py --receipts full_pipeline/brain_reports/full_pipeline_receipts.jsonl



Conclusion

The governance project now includes a robust Triad with unified cost scaling, inference‑window symmetry, receipt‑generation and replay, and a draft periodic transition table.  The next development phase will complete the remaining gates, integrate them into the orchestrator, expand candidate tests, and deploy the full pipeline in the demo environment.  By following this roadmap, the system will provide deterministic, reversible, and auditable governance for AI transitions across all categories.

