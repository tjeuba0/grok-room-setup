from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import re


ROOT = Path(__file__).resolve().parents[1]
HOME_MIRROR = ROOT / "home"
ROOM = HOME_MIRROR / ".config" / "codex-room"
PASEO_TEMPLATE = HOME_MIRROR / ".paseo" / "config.json.template"
SYNC = HOME_MIRROR / ".local" / "bin" / "codex-room-sync"
GROK_SYNC = HOME_MIRROR / ".local" / "bin" / "grok-room-sync"
GROK_LAUNCHER = HOME_MIRROR / ".local" / "bin" / "grok-room"
SESSION_USAGE = ROOT / "scripts" / "session-usage"
WORKFLOW_PILOT_REPORT = ROOT / "scripts" / "workflow-pilot-report"


class SetupShapeTests(unittest.TestCase):
    def test_repository_does_not_own_codex_home(self) -> None:
        self.assertFalse((HOME_MIRROR / ".codex").exists())

    def test_paseo_template_is_valid_and_has_expected_roles(self) -> None:
        config = json.loads(PASEO_TEMPLATE.read_text().replace("@@HOME@@", "/tmp/operator"))
        providers = config["agents"]["providers"]
        room_roles = sorted(name for name in providers if name.startswith("grok-"))
        self.assertEqual(
            room_roles,
            ["grok-lead", "grok-peer", "grok-review", "grok-supervisor"],
        )
        self.assertTrue(providers["grok-supervisor"]["paseoTools"]["enabled"])
        self.assertTrue(providers["grok-lead"]["paseoTools"]["enabled"])
        self.assertFalse(providers["grok-peer"]["paseoTools"]["enabled"])
        self.assertFalse(providers["grok-review"]["paseoTools"]["enabled"])
        self.assertEqual(
            providers["grok-review"]["command"],
            ["/tmp/operator/.local/bin/grok-room", "review"],
        )
        self.assertEqual(
            sorted(profile["id"] for profile in config["daemon"]["agentProfiles"]),
            ["local-writer", "review-fast"],
        )
        self.assertNotIn("review-deep", json.dumps(config))

    def test_role_defaults_are_aligned(self) -> None:
        config = json.loads(PASEO_TEMPLATE.read_text().replace("@@HOME@@", "/tmp/operator"))
        expected = {
            "supervisor": ("grok-4.6", "high"),
            "lead": ("grok-4.6", "high"),
            "peer": ("grok-4.6", "high"),
            "review": ("grok-4.6", "medium"),
        }
        for role, (model, effort) in expected.items():
            overlay_text = (ROOM / "overlays" / f"{role}.config.toml").read_text()
            overlay = dict(
                re.findall(
                    r'^(model|model_reasoning_effort)\s*=\s*"([^"]+)"',
                    overlay_text,
                    flags=re.MULTILINE,
                )
            )
            profile_models = config["agents"]["providers"][f"grok-{role}"]["models"]
            default = next(item for item in profile_models if item.get("isDefault"))
            self.assertEqual(overlay["model"], model)
            self.assertEqual(overlay["model_reasoning_effort"], effort)
            self.assertEqual(default["id"], model)
            thinking_default = next(
                option["id"]
                for option in default["thinkingOptions"]
                if option.get("isDefault")
            )
            self.assertEqual(thinking_default, effort)

        profiles = {
            profile["id"]: profile for profile in config["daemon"]["agentProfiles"]
        }
        self.assertEqual(profiles["local-writer"]["thinkingOptionId"], "high")
        self.assertEqual(profiles["review-fast"]["thinkingOptionId"], "medium")

        launcher = GROK_LAUNCHER.read_text()
        self.assertIn("--no-subagents", launcher)
        self.assertIn('disallowed_tools=Agent', launcher)
        self.assertIn('--disallowed-tools "${disallowed_tools}"', launcher)
        self.assertIn("GROK_SUBAGENTS=0", launcher)

    def test_no_private_state_or_machine_home_is_tracked(self) -> None:
        forbidden_names = {
            "auth.json",
            "daemon-keypair.json",
            "push-tokens.json",
            "server-id",
            "cli-client-id",
        }
        for path in HOME_MIRROR.rglob("*"):
            self.assertNotIn(path.name, forbidden_names)
            if path.is_file():
                self.assertNotIn("/Users/tubakhuym", path.read_text(errors="ignore"))

    def test_installer_renders_home_without_touching_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fake_home = Path(temporary)
            env = os.environ.copy()
            env["HOME"] = str(fake_home)
            subprocess.run(
                [str(ROOT / "scripts" / "install"), "--apply"],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
            paseo_config = fake_home / ".paseo" / "config.json"
            self.assertTrue(paseo_config.is_file())
            self.assertNotIn("@@HOME@@", paseo_config.read_text())
            self.assertIn(str(fake_home / ".local" / "bin" / "grok-room"), paseo_config.read_text())
            protocol = fake_home / ".config" / "codex-room" / "workflow" / "WORKSPACE_PROTOCOL.md"
            self.assertTrue(protocol.is_file())
            self.assertIn("FRONTIER_BRIEF v1", protocol.read_text())
            notebook = fake_home / ".config" / "codex-room" / "workflow" / "SUPERVISOR_NOTEBOOK.md"
            notebook.write_text("# Runtime learning\n")
            second_install = subprocess.run(
                [str(ROOT / "scripts" / "install"), "--apply"],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(notebook.read_text(), "# Runtime learning\n")
            self.assertIn("PRESERVED  ~/.config/codex-room/workflow/SUPERVISOR_NOTEBOOK.md", second_install.stdout)
            self.assertFalse((fake_home / ".codex").exists())
            self.assertFalse((fake_home / ".codex-runtime").exists())

    def test_official_paseo_installer_creates_grok_room_branch_and_links_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fake_home = Path(temporary) / "home"
            source = Path(temporary) / "source"
            remote = Path(temporary) / "upstream.git"
            checkout = Path(temporary) / "paseo-grok-room"
            cli_source = source / "packages" / "cli" / "bin" / "paseo"
            cli_source.parent.mkdir(parents=True)
            cli_source.write_text("#!/usr/bin/env node\n")
            subprocess.run(["git", "init", "-q", "-b", "main", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(
                [
                    "git", "-C", str(source),
                    "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qm", "fixture",
                ],
                check=True,
            )
            subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
            subprocess.run(["git", "-C", str(source), "remote", "add", "origin", str(remote)], check=True)
            subprocess.run(["git", "-C", str(source), "push", "-q", "origin", "main"], check=True)
            verified_commit = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(fake_home),
                    "PASEO_REPO_DIR": str(checkout),
                    "PASEO_UPSTREAM_URL": str(remote),
                    "PASEO_VERIFIED_COMMIT": verified_commit,
                    "PASEO_LIVE_REFERENCE_DIR": str(Path(temporary) / "missing-live"),
                }
            )
            subprocess.run(
                [str(ROOT / "scripts" / "install-paseo-fork")],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )

            link = fake_home / ".local" / "bin" / "paseo"
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), str(checkout / "packages" / "cli" / "bin" / "paseo"))
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(checkout), "branch", "--show-current"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
                "grok-room",
            )
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
                verified_commit,
            )

    def test_session_usage_reports_requests_tools_tokens_and_cost(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "session-usage.jsonl"
        completed = subprocess.run(
            [
                str(SESSION_USAGE),
                "--format",
                "json",
                "--input-rate",
                "5",
                "--cached-input-rate",
                "0.5",
                "--output-rate",
                "30",
                str(fixture),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(completed.stdout)

        self.assertEqual(summary["session_id"], "fixture-session")
        self.assertEqual(summary["timing"]["duration_ms"], 5000)
        self.assertEqual(summary["model_requests"], 2)
        self.assertEqual(summary["tools"]["invocations"], 2)
        self.assertEqual(summary["usage"]["cumulative"]["total_tokens"], 2800)
        self.assertEqual(
            summary["usage"]["final_request"]["context_window_used_tokens"],
            1700,
        )
        self.assertAlmostEqual(summary["estimated_api_cost_usd"], 0.017)

    def test_workflow_pilot_report_counts_only_assistant_markers(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "workflow-pilot.jsonl"
        completed = subprocess.run(
            [str(WORKFLOW_PILOT_REPORT), "--format", "json", str(fixture)],
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(completed.stdout)

        self.assertEqual(summary["assistant_messages_scanned"], 4)
        self.assertEqual(summary["markers"]["FRONTIER_BRIEF v1"], 1)
        self.assertEqual(summary["markers"]["PLAN_RECONCILIATION v1"], 1)
        self.assertEqual(summary["peer_dispositions"]["REOPEN_REQUEST"], 1)
        self.assertEqual(summary["lead_rulings"]["REVISE_PLAN"], 1)
        self.assertEqual(summary["foundation_statuses"]["FOUNDATION_REQUIRED"], 1)
        self.assertEqual(summary["parallel_decisions"]["SERIAL"], 1)
        self.assertEqual(summary["reconciliation_plan_updates"]["yes"], 1)
        self.assertEqual(summary["warnings"], [])

    def test_workflow_pilot_contracts_are_present_in_protocol_and_roles(self) -> None:
        protocol = (ROOM / "workflow" / "WORKSPACE_PROTOCOL.md").read_text()
        for marker in (
            "FRONTIER_BRIEF v1",
            "FOUNDATION_CHECK v1",
            "PEER_DISPOSITION v1",
            "LEAD_RULING v1",
            "PLAN_RECONCILIATION v1",
            "PARALLEL_CHECK v1",
        ):
            self.assertIn(marker, protocol)

        lead = (ROOM / "overlays" / "lead.config.toml").read_text()
        peer = (ROOM / "overlays" / "peer.config.toml").read_text()
        supervisor = (ROOM / "overlays" / "supervisor.config.toml").read_text()
        self.assertIn("FOUNDATION_CHECK v1", lead)
        self.assertIn("PLAN_RECONCILIATION v1", lead)
        self.assertIn("NO_REVIEW", lead)
        self.assertIn("FAST", lead)
        self.assertIn("`DEEP`, `DUAL`, and automatic slow-model fallback are unavailable", lead)
        self.assertIn("`local-writer` profile", lead)
        self.assertIn("`review-fast` profile", lead)
        self.assertIn("review_mode: EXPLORATORY | CLOSEOUT", lead)

        review = (ROOM / "overlays" / "review.config.toml").read_text()
        self.assertIn("review_mode: EXPLORATORY | CLOSEOUT", review)
        self.assertIn("CLOSEOUT_CLEAR", review)
        self.assertIn("CLOSEOUT_FINDINGS", review)
        self.assertIn("Do not report `CLOSEOUT_NO_FINDINGS`", review)
        self.assertIn("Grok Review FAST", review)

        lead = (ROOM / "overlays" / "lead.config.toml").read_text()
        self.assertIn("Every\n`CLOSEOUT` brief uses `review_class: FAST`", lead)
        self.assertIn("`review_model_actual`", lead)
        self.assertIn("do not emit updates that only say no event has arrived", lead)
        self.assertIn("WORKSTREAM_LIFECYCLE v1", lead)

        self.assertIn("Review classes and close-out", protocol)
        self.assertIn("`DEEP`, `DUAL`, and automatic slow-model fallback are intentionally unavailable", protocol)
        self.assertIn("one correction batch", protocol)
        self.assertIn("PEER_DISPOSITION v1", peer)
        self.assertIn("workflow pilot", supervisor)


class GrokRuntimeGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fake_home = self.root / "home"
        self.canonical = self.root / "canonical-grok"
        self.room = self.root / "room-config"
        self.overlays = self.room / "overlays"
        self.workflow = self.room / "workflow"
        self.fake_home.mkdir()
        self.canonical.mkdir()
        self.overlays.mkdir(parents=True)
        self.workflow.mkdir()
        (self.canonical / "auth.json").write_text("{}\n")
        for role in ("supervisor", "lead", "peer", "review"):
            shutil.copyfile(
                ROOM / "overlays" / f"{role}.config.toml",
                self.overlays / f"{role}.config.toml",
            )
        for name in ("WORKSPACE_PROTOCOL.md", "ANTI_PATTERNS.md", "SUPERVISOR_NOTEBOOK.md"):
            (self.workflow / name).write_text(f"# {name}\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_sync(self, role: str) -> Path:
        env = os.environ.copy()
        env["HOME"] = str(self.fake_home)
        env["GROK_ROOM_LAB_ROOT"] = str(self.root)
        subprocess.run(["python3", str(GROK_SYNC), role], check=True, env=env, capture_output=True, text=True)
        return self.root / ".runtime" / role

    def test_all_roles_generate_isolated_grok_homes(self) -> None:
        for role in ("supervisor", "lead", "peer", "review"):
            runtime = self.run_sync(role)
            config = (runtime / "config.toml").read_text()
            profile = (runtime / "agent-profile.md").read_text()
            self.assertIn('[subagents]\nenabled = false', config)
            self.assertIn('[memory]\nenabled = false', config)
            self.assertIn('default_skills_installs_purged = true', config)
            self.assertNotIn('managed_config = false', config)
            self.assertIn('model: grok-4.6', profile)
            self.assertIn(f'name: grok-{role}', profile)
            self.assertTrue((runtime / "auth.json").is_file())
            self.assertFalse((runtime / "managed_config.toml").exists())
            self.assertFalse((runtime / "requirements.toml").exists())
            self.assertTrue((runtime / "hooks").is_dir())
            self.assertTrue((runtime / "hooks-paths").is_file())

    def test_review_is_fast_behaviorally_read_only_and_has_no_orchestration_authority(self) -> None:
        runtime = self.run_sync("review")
        profile = (runtime / "agent-profile.md").read_text()
        self.assertIn("Grok Review FAST", profile)
        self.assertIn("DEEP, DUAL, and", profile)
        self.assertIn("must never create, manage, or delegate", profile)
        self.assertFalse((runtime / "sandbox.toml").exists())
        launcher = GROK_LAUNCHER.read_text()
        self.assertIn("Agent,Edit,Write,MultiEdit", launcher)

    def test_supervisor_initializes_notebook_and_uses_paseo_only(self) -> None:
        runtime = self.run_sync("supervisor")
        self.assertTrue((runtime / "SUPERVISOR_NOTEBOOK.md").is_file())
        profile = (runtime / "agent-profile.md").read_text()
        self.assertIn("only through the Paseo tools", profile)
        self.assertIn("Never use Grok native subagents", profile)


if __name__ == "__main__":
    unittest.main()
