"""Bounded checks for argument parsing, termination, and burnout."""

from collections import Counter
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVENT = re.compile(r"\[?(\d+)\]? (\d+) (has taken a dongle|is compiling|"
                   r"is debugging|is refactoring|burned out)")
STRICT_EVENT = re.compile(r"\d+ \d+ (has taken a dongle|is compiling|"
                          r"is debugging|is refactoring|burned out)")


class CodexionTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = tempfile.TemporaryDirectory(prefix="codexion-test-")
        self.addCleanup(workspace.cleanup)
        self.work = workspace.name

    def call(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(ROOT / "codexion"), *args],
                              capture_output=True, text=True,
                              cwd=self.work, timeout=5)

    def test_both_schedulers_finish_required_compiles(self) -> None:
        for scheduler in ("fifo", "edf"):
            for count in (2, 5):
                with self.subTest(scheduler=scheduler, count=count):
                    result = self.call([str(count), "2000", "10", "10",
                                        "10", "3", "5", scheduler])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertNotIn("burned out", result.stdout)
                    compiled: Counter[int] = Counter()
                    acquired: Counter[int] = Counter()
                    for line in result.stdout.splitlines():
                        event = EVENT.fullmatch(line)
                        if not event:
                            self.assertEqual(line, "OK")
                            continue
                        coder = int(event[2])
                        self.assertTrue(1 <= coder <= count)
                        if event[3] == "has taken a dongle":
                            acquired[coder] += 1
                        if event[3] == "is compiling":
                            self.assertGreaterEqual(acquired[coder], 2)
                            acquired[coder] = 0
                            compiled[coder] += 1
                    self.assertTrue(all(compiled[i] >= 3
                                        for i in range(1, count + 1)))

    def test_one_coder_burns_out_without_compiling(self) -> None:
        for scheduler in ("fifo", "edf"):
            with self.subTest(scheduler=scheduler):
                result = self.call(["1", "30", "10", "10", "10",
                                    "0", "0", scheduler])
                self.assertEqual(result.returncode, 0)
                self.assertNotIn("is compiling", result.stdout)
                self.assertEqual(result.stdout.count("burned out"), 1)
                event = [EVENT.fullmatch(line)
                         for line in result.stdout.splitlines()
                         if "burned out" in line][0]
                self.assertIsNotNone(event)
                if event:
                    self.assertGreaterEqual(int(event[1]), 30)

    def test_invalid_arguments_do_not_crash(self) -> None:
        valid = ["2", "1000", "10", "10", "10", "1", "0", "fifo"]
        cases = [[], valid[:-1], valid + ["extra"]]
        for index, value in [(0, "0"), (0, "-1"), (1, "abc"),
                             (2, "-1"), (5, "2147483648"),
                             (6, ""), (7, "FIFO"), (7, "unknown")]:
            args = valid.copy()
            args[index] = value
            cases.append(args)
        for args in cases:
            with self.subTest(args=args):
                result = self.call(args)
                self.assertGreater(result.returncode, 0)
                self.assertTrue(result.stdout or result.stderr)

    def test_logs_match_subject_format(self) -> None:
        result = self.call(["1", "30", "10", "10", "10", "0", "0", "fifo"])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.splitlines())
        for line in result.stdout.splitlines():
            self.assertRegex(line, STRICT_EVENT)
            self.assertIsNotNone(STRICT_EVENT.fullmatch(line), line)


if __name__ == "__main__":
    unittest.main()
