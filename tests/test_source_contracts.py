from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from adapters import inspect_source
from adapters.bilibili.adapter import BilibiliAdapter
from adapters.local_file.adapter import LocalFileAdapter
from core.contracts import (
    SourceAccessError,
    SourceAdapterDisabledError,
    SourceCapability,
    UnsupportedSourceError,
)


class SourceContractTest(unittest.TestCase):
    def test_local_file_is_normalized_to_absolute_location(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sample = tmp_path / "nested" / "sample.mp4"
            sample.parent.mkdir(parents=True)
            sample.write_bytes(b"")

            old_cwd = Path.cwd()
            try:
                os.chdir(tmp_path)
                descriptor = LocalFileAdapter.inspect(Path("nested") / "sample.mp4")
            finally:
                os.chdir(old_cwd)

            self.assertEqual(descriptor.location, str(sample.resolve()))
            self.assertEqual(descriptor.capabilities, (SourceCapability.LOCAL_MEDIA,))
            self.assertTrue(descriptor.source_id.startswith("local_"))
            self.assertEqual(descriptor.metadata["file_name"], "sample.mp4")

    def test_missing_local_file_raises_source_access_error(self) -> None:
        with self.assertRaises(SourceAccessError):
            LocalFileAdapter.inspect(Path("missing.mp4"))

    def test_bilibili_url_normalizes_to_same_descriptor(self) -> None:
        raw_url = "https://www.bilibili.com/video/BV1Q5411W7RE/?share_source=copy_web#fragment"

        from_url = BilibiliAdapter.inspect(raw_url)
        from_bv = BilibiliAdapter.inspect("BV1Q5411W7RE")

        self.assertEqual(from_url.source_id, "bilibili_BV1Q5411W7RE")
        self.assertEqual(from_url.location, "https://www.bilibili.com/video/BV1Q5411W7RE")
        self.assertEqual(from_url.location, from_bv.location)
        self.assertEqual(from_url.source_id, from_bv.source_id)
        self.assertEqual(
            from_url.capabilities,
            (
                SourceCapability.REMOTE_REFERENCE,
                SourceCapability.NETWORK_REQUIRED,
                SourceCapability.PUBLIC_PLATFORM,
            ),
        )
        self.assertEqual(from_url.metadata["canonical_url"], from_url.location)

    def test_bilibili_url_without_scheme_is_supported(self) -> None:
        descriptor = inspect_source(
            "bilibili.com/video/BV1bbGQ6tEdt/?spm_id_from=333.1007.top_right_bar_window_custom_collection.content.click"
        )

        self.assertEqual(descriptor.platform, "bilibili")
        self.assertEqual(descriptor.source_id, "bilibili_BV1bbGQ6tEdt")
        self.assertEqual(descriptor.location, "https://www.bilibili.com/video/BV1bbGQ6tEdt")

    def test_unsupported_url_raises(self) -> None:
        with self.assertRaises(UnsupportedSourceError):
            inspect_source("https://example.com/video/123")

        with self.assertRaises(UnsupportedSourceError):
            inspect_source("ftp://example.com/video/123")

        with self.assertRaises(UnsupportedSourceError):
            inspect_source("nonsense")

    def test_disabled_bilibili_adapter_raises(self) -> None:
        with self.assertRaises(SourceAdapterDisabledError):
            inspect_source(
                "https://www.bilibili.com/video/BV1Q5411W7RE",
                enabled_inputs={"bilibili": False},
            )
