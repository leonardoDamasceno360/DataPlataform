from dataclasses import asdict, dataclass, field


@dataclass
class ValidationResult:
    file_name: str
    file_hash: str
    file_size_kb: float
    is_valid: bool
    pipeline_name: str | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    detected_columns: list[str] = field(default_factory=list)
    missing_columns: list[str] = field(default_factory=list)
    action_label: str = "Ready"

    def to_dict(self):
        return asdict(self)


@dataclass
class OutputFile:
    path: str
    file_name: str
    rows: int
    created_at: str
    pipeline_name: str

    def to_dict(self):
        return asdict(self)


@dataclass
class PipelineResult:
    pipeline_name: str
    status: str
    output_files: list[OutputFile] = field(default_factory=list)
    rows_generated: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    started_at: str = ""
    finished_at: str = ""
    input_file: str = ""
    file_hash: str = ""
    log_lines: list[str] = field(default_factory=list)

    def to_dict(self):
        payload = asdict(self)
        payload["output_files"] = [
            output.to_dict()
            for output in self.output_files
        ]
        return payload
