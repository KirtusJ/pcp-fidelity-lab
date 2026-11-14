"""Regression checks for extractor-dependent local headers and ZIP repacking."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from zlib import crc32


ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools" / "verify.py"


class ReleaseZip(unittest.TestCase):
    def test_canonical_and_repacked_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            clean = Path(directory) / "clean.zip"
            subprocess.run([sys.executable, str(VERIFY), "--package", str(clean)], check=True)
            subprocess.run([sys.executable, str(VERIFY), "--zip", str(clean)], check=True)
            pin = json.loads((ROOT / "releases" / "0.1.0.json").read_bytes())["canonical_zip"]
            self.assertEqual(hashlib.sha256(clean.read_bytes()).hexdigest(), pin["sha256"])
            with ZipFile(clean) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}

            for case in ("local_name", "compressed", "same_size_header"):
                with self.subTest(case=case):
                    out = Path(directory) / (case + ".zip")
                    with ZipFile(out, "w") as archive:
                        for name, data in files.items():
                            info = ZipInfo(name)
                            info.create_system = 3
                            info.external_attr = 0o100644 << 16
                            if case == "compressed":
                                info.compress_type = ZIP_DEFLATED
                            if case == "same_size_header" and name == "README.md":
                                info.date_time = (1981, 1, 1, 0, 0, 0)
                            if case == "local_name" and name == "README.md":
                                # Info-ZIP Unicode Path (0x7075), present only in the local header.
                                body = struct.pack("<BI", 1, crc32(name.encode())) + b"alternate.md"
                                info.extra = struct.pack("<HH", 0x7075, len(body)) + body
                            archive.writestr(info, data)
                            info.extra = b""  # The central directory retains the canonical names.
                    with ZipFile(out) as archive:
                        self.assertEqual({name: archive.read(name) for name in archive.namelist()}, files)
                    if case == "same_size_header":
                        self.assertEqual(out.stat().st_size, clean.stat().st_size)
                    result = subprocess.run([sys.executable, str(VERIFY), "--zip", str(out)],
                                            text=True, capture_output=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("canonical ZIP:", result.stderr)


if __name__ == "__main__":
    unittest.main()
