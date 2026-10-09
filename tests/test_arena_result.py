"""Synthetic provider records test classification, not model agreement."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/agent-arena/scripts/arena_result.py"
spec = importlib.util.spec_from_file_location("arena_result", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def terminal(**changes):
    record = {"type": "result", "subtype": "success", "is_error": False,
              "session_id": "session-a", "result": "A complete answer.",
              "modelUsage": {"claude-example": {}}}
    record.update(changes)
    return record


class SafeIdTests(unittest.TestCase):
    def test_accepts_allowed_punctuation(self):
        value = "provider/model:release@2026.01+stable-id"
        self.assertEqual(module.safe_id(value), value)

    def test_enforces_length_boundary(self):
        for length, expected in ((160, True), (161, False)):
            with self.subTest(length=length):
                value = "a" * length
                if expected:
                    self.assertEqual(module.safe_id(value), value)
                else:
                    self.assertIsNone(module.safe_id(value))

    def test_rejects_non_string_values(self):
        for value in (None, 1, True, {"id": "model"}, ["model"]):
            with self.subTest(value=value):
                self.assertIsNone(module.safe_id(value))

    def test_rejects_provider_error_prose_and_whitespace(self):
        for value in (
            "provider returned an unexpected error",
            " model-id",
            "model-id ",
            "model-id\nerror details",
        ):
            with self.subTest(value=value):
                self.assertIsNone(module.safe_id(value))


class ResultTests(unittest.TestCase):
    def inspect(self, *records, state="unknown", exit_code=None, pretty=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.jsonl"
            text = json.dumps(records[0], indent=2) if pretty else "\n".join(
                record if isinstance(record, str) else json.dumps(record) for record in records)
            path.write_text(text)
            envelope = module.inspect_result(path, state, exit_code)
            self.assertEqual(path.read_text(), text)  # Input stays untouched.
            self.assertEqual(envelope["review_conclusion"], "unassessed")
            self.assertNotIn("substantive", envelope.values())
            return envelope

    def test_complete_result_is_only_a_candidate(self):
        result = self.inspect(terminal(), state="exited", exit_code=0)
        self.assertEqual(result["answer_state"], "candidate_complete")
        self.assertEqual(result["result_reference"]["line"], 1)
        self.assertIsNone(result["failure_reason"])

    def test_success_and_error_cannot_be_successful_review(self):
        result = self.inspect(terminal(is_error=True, error={"code": "quota_exceeded"}), state="exited", exit_code=0)
        self.assertEqual(result["failure_reason"], "quota")
        self.assertEqual(result["answer_state"], "none")
        self.assertFalse(result["terminal_success_observed"])

    def test_error_prose_without_structured_code_is_unknown(self):
        result = self.inspect(terminal(is_error=True, result="Quota exhausted."))
        self.assertEqual(result["failure_reason"], "unknown")

    def test_successful_answer_mentioning_quota_is_not_a_quota_failure(self):
        result = self.inspect(terminal(result="The quota logic in the code has a bug."))
        self.assertIsNone(result["failure_reason"])

    def test_partial_output_is_not_running_without_host_observation(self):
        assistant = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Observed defect"}]}}
        result = self.inspect(assistant)
        self.assertEqual(result["execution_state"], "unknown")
        self.assertEqual(result["answer_state"], "partial")
        self.assertFalse(result["terminal_result_observed"])

    def test_queued_poll_is_not_timeout(self):
        result = self.inspect(state="queued")
        self.assertEqual(result["execution_state"], "queued")
        self.assertIsNone(result["failure_reason"])

    def test_damage_before_terminal_preserves_complete_candidate(self):
        result = self.inspect("{broken earlier line", terminal())
        self.assertEqual(result["parse_state"], "partial")
        self.assertEqual(result["answer_state"], "candidate_complete")

    def test_unparsed_records_after_terminal_do_not_certify_latest_call(self):
        for trailing in ("{truncated next result", "[]", {"unknown": "new activity"}):
            with self.subTest(trailing=trailing):
                result = self.inspect(terminal(), trailing)
                self.assertEqual(result["parse_state"], "partial")
                self.assertEqual(result["answer_state"], "partial")
                self.assertFalse(result["terminal_success_observed"])
                self.assertIsNotNone(result["result_reference"])
                self.assertIn("unparsed_record_after_terminal_manual_review_required", result["issues"])

    def test_broken_separate_digest_does_not_change_raw_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            digest = Path(directory) / "summary.json"
            digest.write_text("{broken digest")
            result = self.inspect(terminal())
            self.assertEqual(result["answer_state"], "candidate_complete")
            self.assertEqual(result["parse_state"], "parsed")

    def test_truncated_utf8_keeps_recoverable_result_and_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.jsonl"
            raw = json.dumps(terminal()).encode() + b'\n{"type":"assistant","message":{"content":"\xe4\xb8'
            path.write_bytes(raw)
            result = module.inspect_result(path)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(result["parse_state"], "partial")
            self.assertEqual(result["answer_state"], "partial")
            self.assertIsNotNone(result["result_reference"])

    def test_last_terminal_error_does_not_hide_previous_attempts(self):
        result = self.inspect(terminal(), terminal(subtype="error_max_turns", is_error=True))
        self.assertEqual(result["failure_reason"], "error_max_turns")
        self.assertEqual(result["result_count"], 2)
        self.assertEqual(result["result_reference"]["line"], 2)

    def test_mixed_sessions_require_manual_reconciliation(self):
        result = self.inspect(terminal(), terminal(session_id="session-b"))
        self.assertEqual(result["answer_state"], "partial")
        self.assertIn("multiple_sessions_manual_review_required", result["issues"])

    def test_new_assistant_after_terminal_is_not_complete(self):
        result = self.inspect(terminal(), {"type": "assistant", "message": {"content": []}})
        self.assertEqual(result["answer_state"], "partial")

    def test_new_request_or_stream_after_old_result_needs_reconciliation(self):
        for event in ({"type": "user", "message": {"content": "next request"}},
                      {"type": "stream_event", "event": {"type": "message_start"}},
                      {"type": "system", "subtype": "init"}):
            with self.subTest(event=event):
                result = self.inspect(terminal(), event)
                self.assertEqual(result["answer_state"], "partial")
                self.assertFalse(result["terminal_success_observed"])

    def test_pretty_document_and_missing_metadata(self):
        result = self.inspect(terminal(session_id=None, modelUsage=None), pretty=True)
        self.assertEqual(result["answer_state"], "candidate_complete")
        self.assertEqual(result["model_identity_verification"], "unknown")
        self.assertIsNone(result["result_reference"]["line"])

    def test_unknown_terminal_is_not_assumed_success(self):
        result = self.inspect(terminal(subtype="future_variant", is_error=None))
        self.assertEqual(result["failure_reason"], "unknown")
        self.assertEqual(result["answer_state"], "none")

    def test_wrapper_failure_preserved_with_answer(self):
        result = self.inspect(terminal(), state="exited", exit_code=7)
        self.assertEqual(result["answer_state"], "candidate_complete")
        self.assertEqual(result["failure_reason"], "unknown")

    def test_raw_answer_and_error_secret_not_copied_to_envelope(self):
        result = self.inspect(terminal(is_error=True, result="SECRET_TOKEN", error={"code": "SECRET_TOKEN"}))
        self.assertNotIn("SECRET_TOKEN", json.dumps(result))

    def test_unsupported_shape_is_not_a_review(self):
        result = self.inspect({"text": "complete"})
        self.assertEqual(result["parse_state"], "failed")
        self.assertEqual(result["answer_state"], "none")

    def test_multiline_json_starting_with_a_field_is_supported(self):
        raw = '{"type":"result",\n"subtype":"success","is_error":false,"result":"answer"}'
        result = self.inspect(raw)
        self.assertEqual(result["answer_state"], "candidate_complete")
        self.assertEqual(result["parse_state"], "parsed")

    def test_error_after_success_preserves_failure_and_coverage_gap(self):
        result = self.inspect(terminal(), {"type": "error", "error": {"type": "stream_error"}})
        self.assertEqual(result["failure_reason"], "transport")
        self.assertEqual(result["answer_state"], "partial")

    def test_streaming_text_before_terminal_is_preserved_as_partial(self):
        result = self.inspect({"type": "stream_event", "event": {
            "type": "content_block_delta", "delta": {"type": "text_delta", "text": "partial answer"}}})
        self.assertEqual(result["answer_state"], "partial")
        self.assertFalse(result["terminal_result_observed"])

    def test_error_event_recovered_by_later_terminal_stays_in_history(self):
        result = self.inspect({"type": "error", "error": {"type": "stream_error"}}, terminal())
        self.assertIsNone(result["failure_reason"])
        self.assertEqual(result["observed_error_events"], [{"line": 1, "failure_reason": "transport"}])


if __name__ == "__main__":
    unittest.main()
