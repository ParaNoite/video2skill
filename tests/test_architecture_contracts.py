from dataclasses import fields
from pathlib import Path
import unittest

from core.contracts import (
    AuditReport,
    EvidenceUnit,
    KnowledgeUnit,
    SourceCapability,
    SourceDescriptor,
    TaskManifest,
    TaskState,
)


class ArchitectureContractTest(unittest.TestCase):
    def test_core_objects_include_required_fields(self) -> None:
        self.assertIn("task_id", {field.name for field in fields(TaskManifest)})
        self.assertIn("source", {field.name for field in fields(TaskManifest)})
        self.assertIn("state", {field.name for field in fields(TaskManifest)})
        self.assertIn("task_dir", {field.name for field in fields(TaskManifest)})
        self.assertIn("cache_dir", {field.name for field in fields(TaskManifest)})
        self.assertIn("output_dir", {field.name for field in fields(TaskManifest)})

        self.assertIn("time_range", {field.name for field in fields(EvidenceUnit)})
        self.assertIn("sources", {field.name for field in fields(EvidenceUnit)})
        self.assertIn("confidence", {field.name for field in fields(EvidenceUnit)})

        self.assertIn("evidence_refs", {field.name for field in fields(KnowledgeUnit)})
        self.assertIn("confidence", {field.name for field in fields(KnowledgeUnit)})

        self.assertIn("coverage", {field.name for field in fields(AuditReport)})
        self.assertIn("decision", {field.name for field in fields(AuditReport)})

    def test_supported_task_states(self) -> None:
        self.assertEqual(
            [state.value for state in TaskState],
            ["CREATED", "ANALYZING", "PROCESSING", "REVIEWING", "DONE", "FAILED"],
        )

    def test_descriptor_is_path_safe(self) -> None:
        descriptor = SourceDescriptor(
            platform="local_file",
            source_id="local_sample",
            title="sample",
            location=str(Path("sample.mp4").resolve()),
            is_local_file=True,
            capabilities=(SourceCapability.LOCAL_MEDIA,),
        )
        self.assertTrue(descriptor.is_local_file)
        self.assertIn("capabilities", {field.name for field in fields(SourceDescriptor)})
