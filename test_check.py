import unittest
from check import summarize, validate


def record(status="completed", mentioned=True):
    return dict(id="example", engine="illustrative-engine", language="en",
                prompt_id="demo-prompt", observed_at="2026-10-23T00:00:00Z",
                status=status, brand_mentioned=mentioned)


class ObservationTests(unittest.TestCase):
    def test_timeout_is_not_a_negative_mention(self):
        rows = [validate(record()), validate(record(mentioned=False)),
                validate(record("timeout", None))]
        result = summarize(rows)
        self.assertEqual(result["observed_mention_rate"], 0.5)
        self.assertAlmostEqual(result["completion_fraction"], 2 / 3)

    def test_all_failures_produce_unknown_rate(self):
        self.assertIsNone(summarize([validate(record("failed", None))])["observed_mention_rate"])

    def test_completed_needs_an_actual_boolean(self):
        for value in (None, "false", 0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate(record(mentioned=value))

    def test_failure_cannot_claim_a_negative(self):
        with self.assertRaises(ValueError):
            validate(record("failed", False))

    def test_timestamp_must_include_timezone(self):
        row = record()
        row["observed_at"] = "2026-10-23T00:00:00"
        with self.assertRaises(ValueError):
            validate(row)

    def test_empty_dataset_is_unknown(self):
        self.assertIsNone(summarize([])["observed_mention_rate"])


if __name__ == "__main__":
    unittest.main()
