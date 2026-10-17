from __future__ import annotations

import copy
import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_contracts_routing", REPO_ROOT / "scripts" / "check-contracts.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load scripts/check-contracts.py")
CHECK_CONTRACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CONTRACTS)


def load_skills() -> dict[str, dict[str, object]]:
    with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
        return tomllib.load(handle)["skills"]


class RoutingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills = load_skills()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.routing_id, routing_entry = next(
            (skill_id, entry)
            for skill_id, entry in self.skills.items()
            if entry.get("routing_contract")
        )
        relative = Path("skills") / self.routing_id / str(routing_entry["routing_contract"])
        source_path = REPO_ROOT / relative
        self.contract_path = self.root / relative
        self.contract_path.parent.mkdir(parents=True)
        self.contract_path.write_text(
            source_path.read_text(encoding="utf-8"), encoding="utf-8"
        )
        with source_path.open("rb") as handle:
            self.routing_contract = tomllib.load(handle)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, skills: dict[str, object] | None = None) -> list[str]:
        return CHECK_CONTRACTS.validate_routing_contracts(
            skills or self.skills,
            self.root,
        )

    def validate_scope(self, routing_contract: dict[str, object]) -> list[str]:
        return CHECK_CONTRACTS.validate_scope_contract(
            self.skills, routing_contract, REPO_ROOT
        )

    def first_handoff(self, routing: dict[str, object]) -> dict[str, object]:
        return next(
            cluster["handoffs"][0]
            for cluster in routing["clusters"]
            if cluster.get("handoffs")
        )

    def test_current_scope_contract_is_complete(self) -> None:
        self.assertEqual([], self.validate_scope(self.routing_contract))

    def test_exactly_one_routing_contract_is_required(self) -> None:
        skills = copy.deepcopy(self.skills)
        del skills[self.routing_id]["routing_contract"]

        errors = self.validate(skills)

        self.assertTrue(
            any("exactly one routing_contract" in error for error in errors)
        )

    def test_schema_version_and_retired_tables_are_rejected(self) -> None:
        current = self.contract_path.read_text(encoding="utf-8")
        self.contract_path.write_text(
            current.replace("version = 2", "version = 1", 1)
            + '\n[support_routes]\nresponse-shape = "output-styles"\n',
            encoding="utf-8",
        )

        errors = self.validate()

        self.assertTrue(any("version = 2" in error for error in errors))
        self.assertTrue(any("retired table: support_routes" in error for error in errors))

    def test_cluster_ids_questions_and_members_are_structural(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        duplicate = copy.deepcopy(routing["clusters"][0])
        duplicate["question"] = " "
        duplicate["members"] = ["missing", "none", "review-design"]
        routing["clusters"].append(duplicate)

        errors = self.validate_scope(routing)

        self.assertTrue(any("duplicate cluster id" in error for error in errors))
        self.assertTrue(any("non-empty question" in error for error in errors))
        self.assertTrue(any("unknown skill: missing" in error for error in errors))
        self.assertTrue(any("member cannot be none" in error for error in errors))
        self.assertTrue(
            any("composition-only evaluator" in error for error in errors)
        )

    def test_handoff_requires_one_resolvable_receiver(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        handoffs = next(
            cluster["handoffs"]
            for cluster in routing["clusters"]
            if len(cluster.get("handoffs", [])) >= 3
        )
        handoffs[0]["owner"] = ["plan-change", "design-change"]
        handoffs[1]["owner"] = f"{self.routing_id}:missing-method"
        handoffs[2]["instead_of"] = [handoffs[2]["owner"]]

        errors = self.validate_scope(routing)

        self.assertTrue(any("exactly one owner" in error for error in errors))
        self.assertTrue(any("unknown method" in error for error in errors))
        self.assertTrue(
            any("owner cannot also be a replaced candidate" in error for error in errors)
        )

    def test_handoff_requires_a_situation_and_replaced_candidates(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        handoff = self.first_handoff(routing)
        handoff["when"] = ""
        handoff["instead_of"] = []

        errors = self.validate_scope(routing)

        self.assertTrue(any("non-empty when" in error for error in errors))
        self.assertTrue(any("at least one candidate" in error for error in errors))

    def test_none_is_a_valid_receiver(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        self.first_handoff(routing)["owner"] = "none"

        self.assertEqual([], self.validate_scope(routing))

    def test_replaced_candidates_may_include_none_and_evaluators(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        handoff = self.first_handoff(routing)
        handoff["instead_of"] = [*handoff["instead_of"], "none", "review-implementation"]

        self.assertEqual([], self.validate_scope(routing))

    def test_uncovered_selectable_skill_is_rejected(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        for cluster in routing["clusters"]:
            cluster["members"] = [
                member for member in cluster["members"] if member != "analyze-project"
            ]

        errors = self.validate_scope(routing)

        self.assertTrue(
            any(
                "analyze-project: selectable skill must be a member" in error
                for error in errors
            )
        )


class SelectionProbeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skills = load_skills()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate_corpus(self, text: str) -> list[str]:
        path = self.root / CHECK_CONTRACTS.PROBE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return CHECK_CONTRACTS.validate_selection_probes(self.skills, self.root)

    def test_current_probe_corpus_is_valid(self) -> None:
        self.assertEqual(
            [], CHECK_CONTRACTS.validate_selection_probes(self.skills, REPO_ROOT)
        )

    def test_probe_ids_and_selection_targets_must_resolve(self) -> None:
        probe = """
[[probes]]
id = "same-id"
request = "Request."
primary = "missing"
overlays = ["review-plan"]
counterexample = "Counterexample."
counterexample_primary = "none"
"""
        errors = self.validate_corpus(probe + probe)

        self.assertTrue(any("duplicate probe id: same-id" in error for error in errors))
        self.assertTrue(any("unknown skill: missing" in error for error in errors))
        self.assertTrue(any("composition-only evaluator" in error for error in errors))

    def test_counterexample_must_expect_a_different_selection(self) -> None:
        errors = self.validate_corpus(
            """
[[probes]]
id = "no-contrast"
request = "Fix the deploy script."
primary = "implement-change"
overlays = ["shell-guidelines"]
counterexample = "Fix the other deploy script."
counterexample_primary = "implement-change"
counterexample_overlays = ["shell-guidelines"]
"""
        )

        self.assertTrue(
            any("counterexample must expect a different selection" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
