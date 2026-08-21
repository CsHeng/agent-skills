from __future__ import annotations

import copy
import importlib.util
import tempfile
import textwrap
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_contracts", REPO_ROOT / "scripts" / "check-contracts.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load scripts/check-contracts.py")
CHECK_CONTRACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CONTRACTS)


VALID_CONTRACT = """
version = 1

[workflow]
id = "implement-change"

[[nodes]]
id = "implement-change"
role = "controller"
owns_repair_loop = true

[[nodes]]
id = "review-change"
role = "gate"

[[nodes]]
id = "review-implementation"
role = "evaluator"

[[edges]]
from = "implement-change"
to = "review-change"

[[edges]]
from = "review-change"
to = "review-implementation"

[[forbidden_edges]]
from = "review-implementation"
to = "implement-change"

[repair]
owner = "implement-change"
initial_review_passes = 1
focused_verification_passes = 1
additional_same_slice_repair_attempts = 1
"""


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.skills = {
            "implement-change": {
                "category": "workflow",
                "lifecycle_owner": True,
                "runtime_contract": "references/workflow.toml",
            },
            "review-change": {
                "category": "workflow",
                "lifecycle_owner": True,
            },
            "review-implementation": {
                "category": "review-component",
                "lifecycle_owner": False,
            },
        }
        self.contract_path = self.root / "skills/implement-change/references/workflow.toml"
        self.contract_path.parent.mkdir(parents=True)
        self.contract_path.write_text(textwrap.dedent(VALID_CONTRACT).lstrip(), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, skills: dict[str, object] | None = None) -> list[str]:
        return CHECK_CONTRACTS.validate_runtime_contracts(skills or self.skills, self.root)

    def rewrite(self, old: str, new: str) -> None:
        current = self.contract_path.read_text(encoding="utf-8")
        self.contract_path.write_text(current.replace(old, new), encoding="utf-8")

    def test_valid_controller_contract(self) -> None:
        self.assertEqual([], self.validate())

    def test_missing_contract_is_rejected(self) -> None:
        self.contract_path.unlink()
        self.assertTrue(any("does not exist" in error for error in self.validate()))

    def test_unknown_node_is_rejected(self) -> None:
        self.rewrite('id = "review-implementation"', 'id = "unknown-reviewer"')
        self.assertTrue(any("unknown runtime node" in error for error in self.validate()))

    def test_evaluator_reverse_call_is_rejected(self) -> None:
        self.rewrite(
            "[repair]\nowner",
            '[[edges]]\nfrom = "review-implementation"\nto = "implement-change"\n\n[repair]\nowner',
        )
        errors = self.validate()
        self.assertTrue(any("evaluator cannot invoke" in error for error in errors))
        self.assertTrue(any("contains a cycle" in error for error in errors))

    def test_multiple_repair_owners_are_rejected(self) -> None:
        self.rewrite('id = "review-change"\nrole = "gate"', 'id = "review-change"\nrole = "gate"\nowns_repair_loop = true')
        self.assertTrue(any("exactly one" in error for error in self.validate()))

    def test_repair_owners_across_two_contracts_are_rejected(self) -> None:
        second_source = "alternate-implement-change"
        second_path = self.root / "skills" / second_source / "references/workflow.toml"
        second_path.parent.mkdir(parents=True)
        second_path.write_text(
            textwrap.dedent(VALID_CONTRACT)
            .lstrip()
            .replace("implement-change", "alternate-implement-change"),
            encoding="utf-8",
        )
        skills = copy.deepcopy(self.skills)
        skills["alternate-implement-change"] = {
            "category": "workflow",
            "lifecycle_owner": True,
            "runtime_contract": "references/workflow.toml",
        }

        errors = self.validate(skills)

        self.assertTrue(any("global runtime contracts" in error for error in errors))

    def test_more_than_one_additional_repair_attempt_is_rejected(self) -> None:
        self.rewrite(
            "additional_same_slice_repair_attempts = 1",
            "additional_same_slice_repair_attempts = 2",
        )
        self.assertTrue(any("at most one additional" in error for error in self.validate()))

    def test_cycle_is_rejected(self) -> None:
        self.rewrite(
            "[repair]\nowner",
            '[[edges]]\nfrom = "review-change"\nto = "implement-change"\n\n[repair]\nowner',
        )
        self.assertTrue(any("contains a cycle" in error for error in self.validate()))

    def test_execution_contract_assigns_logical_and_runtime_ownership(self) -> None:
        contract_path = REPO_ROOT / "skills/implement-change/references/workflow.toml"
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)

        execution = contract["execution"]
        self.assertEqual("plan-change", execution["topology_owner"])
        self.assertEqual("implement-change", execution["runtime_binding_owner"])
        self.assertEqual("semantic-routing", execution["default_model_policy"])
        self.assertEqual(["deep", "balanced", "fast"], execution["execution_profiles"])
        self.assertEqual(["deep", "standard", "light"], execution["reasoning_profiles"])

    def test_inherit_main_preserves_topology_and_conditional_fallback(self) -> None:
        contract_path = REPO_ROOT / "skills/implement-change/references/workflow.toml"
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)

        execution = contract["execution"]
        self.assertIn("inherit-main", execution["allowed_model_policies"])
        self.assertTrue(execution["inherit_main_preserves_topology"])
        self.assertTrue(execution["allowed_parallel_may_serialize"])
        self.assertTrue(execution["allowed_parallel_serialization_requires_evidence"])
        self.assertEqual("maximal-safe-ready-set", execution["approved_parallel_selection"])
        self.assertTrue(execution["requires_cleared_planning_prerequisites"])
        self.assertEqual("parallel_capacity_required", execution["required_parallel_capacity_exit"])

    def test_native_routing_uses_parent_baseline_without_an_explorer_ceiling(self) -> None:
        contract_path = REPO_ROOT / "skills/implement-change/references/workflow.toml"
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)

        explorer = contract["explorer"]
        self.assertEqual("parent-session", explorer["physical_baseline"])
        self.assertEqual("minimum-only-no-ceiling", explorer["reasoning_policy"])
        self.assertEqual(
            ["parent-inherit", "effort-only-uplift", "model-plus-effort-uplift"],
            explorer["semantic_routing_shapes"],
        )
        self.assertEqual("typed-stop-no-downgrade", explorer["required_uplift_rejection"])
        native = contract["runtime_binding"]["codex_native"]
        self.assertEqual(
            ["parent_reasoning_effort", "required_minimum_reasoning_effort"],
            native["reasoning_evidence"],
        )
        self.assertTrue(native["monotonic_reasoning_required"])
        for removed in (
            "role_cost",
            "default_effort",
            "max_effort",
            "semantic_routing_default_effort",
            "semantic_routing_max_effort",
            "rejected_efforts",
        ):
            self.assertNotIn(removed, explorer)

    def test_workers_cannot_recursively_delegate_or_assume_controller_ownership(self) -> None:
        contract_path = REPO_ROOT / "skills/implement-change/references/workflow.toml"
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)

        workers = contract["workers"]
        for field in (
            "delegated_recursion",
            "may_widen_scope",
            "may_integrate_peer_work",
            "may_adjudicate_review",
            "may_repair",
            "may_decide_continuation",
            "custom_role_guidance_may_pin_model",
        ):
            self.assertFalse(workers[field], field)
        self.assertTrue(contract["execution"]["controller_converges_batches"])
        controller_nodes = [node for node in contract["nodes"] if node["role"] == "controller"]
        repair_nodes = [node for node in contract["nodes"] if node.get("owns_repair_loop")]
        self.assertEqual(["implement-change"], [node["id"] for node in controller_nodes])
        self.assertEqual(["implement-change"], [node["id"] for node in repair_nodes])
        self.assertEqual("implement-change", contract["repair"]["owner"])

    def test_external_touch_contract_is_main_owned_and_backend_excluded(self) -> None:
        contract_path = REPO_ROOT / "skills/implement-change/references/workflow.toml"
        with contract_path.open("rb") as handle:
            contract = tomllib.load(handle)

        external = contract["external_touch"]
        self.assertEqual("exact-existing-files-v1", external["policy"])
        self.assertEqual("main", external["actor"])
        self.assertEqual("forbidden", external["delegation"])
        self.assertEqual("forbidden", external["parallel"])
        self.assertTrue(external["broker_only"])
        self.assertTrue(external["immutable_baseline"])
        self.assertFalse(external["automatic_rollback"])
        self.assertFalse(external["backend_envelope_exposure"])

    def test_external_touch_workflow_surfaces_preserve_lifecycle_ownership(self) -> None:
        surfaces = {
            "plan": REPO_ROOT / "skills/plan-change/SKILL.md",
            "implement": REPO_ROOT / "skills/implement-change/SKILL.md",
            "review": REPO_ROOT / "skills/review-change/SKILL.md",
            "review_impl": REPO_ROOT / "skills/review-implementation/SKILL.md",
            "truth": REPO_ROOT / "skills/sync-truth/SKILL.md",
        }
        content = {name: path.read_text(encoding="utf-8") for name, path in surfaces.items()}
        self.assertIn("external_impl_file_refs", content["plan"])
        self.assertIn("repository-only bootstrap plan", content["plan"])
        self.assertIn("external-baseline", content["implement"])
        self.assertIn("parent-linked broker intent", content["implement"])
        self.assertIn("reviewer remains read-only", content["review"])
        self.assertIn("metadata-only", content["review_impl"])
        self.assertIn("without rereading the current external file", content["truth"])


if __name__ == "__main__":
    unittest.main()
