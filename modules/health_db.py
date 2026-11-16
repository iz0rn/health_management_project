"""건강정보 레코드와 JSON, CSV, TXT, Pickle 저장소를 제공합니다."""

# AI 사용 기록
# - AI: OpenAI Copilot SDK
# - 목적: 모듈 1(건강정보 레코드 및 4종 파일 저장/불러오기) 구현
# - 프롬프트: "첨부 지정프로젝트 요구사항에 따라 README를 읽고 모듈 1을 구현해줘."
# - 사용자: 과제 제출자(이름 미제공)
# - 사용일: 2026-11-16

from __future__ import annotations

import csv
import json
import math
import pickle
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, ClassVar


@dataclass
class HealthRecord:
    """한 사람의 인적 정보와 BMI 건강정보를 나타냅니다."""

    id: str
    name: str
    birth_year: int
    gender: str
    height: float
    weight: float
    bmi: float = field(init=False)
    status: str = field(init=False)

    FIELDS: ClassVar[tuple[str, ...]] = (
        "id",
        "name",
        "birth_year",
        "gender",
        "height",
        "weight",
        "bmi",
        "status",
    )

    def __post_init__(self) -> None:
        """필수 입력을 검증하고 키와 체중으로 BMI 및 상태를 계산합니다."""
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("식별번호는 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("이름은 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(self.gender, str) or not self.gender.strip():
            raise ValueError("성별은 비어 있지 않은 문자열이어야 합니다.")
        if isinstance(self.birth_year, bool) or not isinstance(self.birth_year, int):
            raise ValueError("생년은 정수로 입력해야 합니다.")
        if self.birth_year <= 0:
            raise ValueError("생년은 0보다 커야 합니다.")

        self.name = self.name.strip()
        self.gender = self.gender.strip()
        self.height = self._positive_number(self.height, "키")
        self.weight = self._positive_number(self.weight, "몸무게")
        self.bmi = round(self.weight / (self.height / 100) ** 2, 2)
        self.status = self._classify_bmi(self.bmi)

    @staticmethod
    def _positive_number(value: Any, label: str) -> float:
        """키 또는 몸무게가 유한한 양수인지 확인합니다."""
        if isinstance(value, bool):
            raise ValueError(f"{label}는 0보다 큰 숫자여야 합니다.")
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{label}는 숫자로 입력해야 합니다.") from error
        if not math.isfinite(number) or number <= 0:
            raise ValueError(f"{label}는 0보다 큰 유한한 숫자여야 합니다.")
        return number

    @staticmethod
    def _classify_bmi(bmi: float) -> str:
        """BMI 값에 따라 저체중, 정상, 과체중 또는 비만을 반환합니다."""
        if bmi < 18.5:
            return "저체중"
        if bmi < 23:
            return "정상"
        if bmi < 25:
            return "과체중"
        return "비만"

    def to_dict(self) -> dict[str, Any]:
        """파일 저장과 비교에 사용할 딕셔너리를 반환합니다."""
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthRecord:
        """딕셔너리에서 레코드를 생성하고 BMI를 다시 계산합니다."""
        required_fields = ("id", "name", "birth_year", "gender", "height", "weight")
        missing_fields = [key for key in required_fields if key not in data]
        if missing_fields:
            raise ValueError(f"필수 필드가 없습니다: {', '.join(missing_fields)}")

        birth_year = data["birth_year"]
        if isinstance(birth_year, bool):
            raise ValueError("생년은 정수로 입력해야 합니다.")
        try:
            parsed_birth_year = int(birth_year)
        except (TypeError, ValueError) as error:
            raise ValueError("생년은 정수로 입력해야 합니다.") from error
        if isinstance(birth_year, float) and not birth_year.is_integer():
            raise ValueError("생년은 정수로 입력해야 합니다.")

        return cls(
            id=data["id"],
            name=data["name"],
            birth_year=parsed_birth_year,
            gender=data["gender"],
            height=data["height"],
            weight=data["weight"],
        )


class HealthRecordManager:
    """건강정보 목록을 관리하고 네 가지 파일 형식으로 저장합니다."""

    FORMATS: ClassVar[tuple[str, ...]] = ("json", "csv", "txt", "pickle")
    FILE_NAMES: ClassVar[dict[str, str]] = {
        "json": "health_data.json",
        "csv": "health_data.csv",
        "txt": "health_data.txt",
        "pickle": "health_data.pkl",
    }

    def __init__(
        self,
        records: list[HealthRecord] | None = None,
        data_dir: str | Path | None = None,
    ) -> None:
        """레코드 목록과 저장 폴더를 준비합니다."""
        self.records = list(records) if records is not None else []
        if any(not isinstance(record, HealthRecord) for record in self.records):
            raise TypeError("records에는 HealthRecord 객체만 넣을 수 있습니다.")
        self._check_unique_ids(self.records)
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parent.parent / "data"
        )

    @staticmethod
    def _check_unique_ids(records: list[HealthRecord]) -> None:
        """중복된 환자식별번호가 있는지 확인합니다."""
        ids = [record.id for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError("환자식별번호가 중복된 레코드가 있습니다.")

    def _next_id(self) -> str:
        """현재 연도 기준으로 아직 사용하지 않은 식별번호를 생성합니다."""
        year = date.today().year
        pattern = re.compile(rf"^P{year}-(\d+)$")
        used_numbers = [
            int(match.group(1))
            for record in self.records
            if (match := pattern.fullmatch(record.id)) is not None
        ]
        next_number = max(used_numbers, default=0) + 1
        return f"P{year}-{next_number:04d}"

    def add_record(
        self,
        name: str,
        birth_year: int,
        gender: str,
        height: float,
        weight: float,
    ) -> HealthRecord:
        """고유 ID를 발급해 레코드를 목록에 추가합니다."""
        record = HealthRecord(
            id=self._next_id(),
            name=name,
            birth_year=birth_year,
            gender=gender,
            height=height,
            weight=weight,
        )
        self.records.append(record)
        return record

    def display_records(self, records: list[HealthRecord] | None = None) -> None:
        """지정한 레코드 목록(기본값: 전체)을 표 형태로 출력합니다."""
        selected_records = self.records if records is None else records
        headers = HealthRecord.FIELDS
        print(" | ".join(headers))
        print("-" * (len(" | ".join(headers))))
        for record in selected_records:
            print(" | ".join(str(value) for value in record.to_dict().values()))
        if not selected_records:
            print("(등록된 건강정보가 없습니다.)")

    def _resolve_path(self, file_format: str, path: str | Path | None) -> Path:
        """파일 형식을 확인하고 저장 또는 불러올 경로를 결정합니다."""
        normalized_format = file_format.lower()
        if normalized_format not in self.FORMATS:
            expected = ", ".join(self.FORMATS)
            raise ValueError(f"지원하지 않는 파일 형식입니다. 지원 형식: {expected}")
        if path is not None:
            return Path(path)
        return self.data_dir / self.FILE_NAMES[normalized_format]

    def save(self, file_format: str, path: str | Path | None = None) -> Path:
        """현재 레코드 전체를 지정한 파일 형식으로 저장합니다."""
        normalized_format = file_format.lower()
        output_path = self._resolve_path(normalized_format, path)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if normalized_format == "pickle":
                with output_path.open("wb") as file:
                    pickle.dump(self.records, file)
            else:
                records = [record.to_dict() for record in self.records]
                with output_path.open("w", encoding="utf-8", newline="") as file:
                    if normalized_format == "json":
                        json.dump(records, file, ensure_ascii=False, indent=2)
                        file.write("\n")
                    elif normalized_format == "csv":
                        writer = csv.DictWriter(file, fieldnames=HealthRecord.FIELDS)
                        writer.writeheader()
                        writer.writerows(records)
                    else:
                        writer = csv.writer(file)
                        writer.writerows(
                            [record[field] for field in HealthRecord.FIELDS]
                            for record in records
                        )
        except (OSError, csv.Error, TypeError, pickle.PickleError) as error:
            raise StorageError(f"{output_path} 저장에 실패했습니다: {error}") from error
        return output_path

    def load(
        self, file_format: str, path: str | Path | None = None
    ) -> list[HealthRecord]:
        """파일을 읽어 레코드 목록에 반영하고 그 목록을 반환합니다."""
        normalized_format = file_format.lower()
        input_path = self._resolve_path(normalized_format, path)
        if not input_path.exists():
            self.records = []
            return self.records

        try:
            if normalized_format == "pickle":
                with input_path.open("rb") as file:
                    loaded_data = pickle.load(file)
                records = self._records_from_pickle(loaded_data)
            else:
                with input_path.open("r", encoding="utf-8", newline="") as file:
                    if normalized_format == "json":
                        loaded_data = json.load(file)
                        records = self._records_from_dicts(loaded_data)
                    elif normalized_format == "csv":
                        reader = csv.DictReader(file)
                        if reader.fieldnames is None:
                            records = []
                        else:
                            records = self._records_from_dicts(list(reader))
                    else:
                        rows = csv.reader(file)
                        records = self._records_from_txt_rows(rows)
        except (
            OSError,
            UnicodeError,
            csv.Error,
            json.JSONDecodeError,
            EOFError,
            pickle.UnpicklingError,
            AttributeError,
            ImportError,
            IndexError,
            TypeError,
            ValueError,
        ) as error:
            raise StorageError(f"{input_path} 불러오기에 실패했습니다: {error}") from error

        self._check_unique_ids(records)
        self.records = records
        return self.records

    @staticmethod
    def _records_from_dicts(data: Any) -> list[HealthRecord]:
        """JSON 또는 CSV 레코드 배열을 HealthRecord 목록으로 변환합니다."""
        if not isinstance(data, list):
            raise ValueError("저장된 데이터의 최상위 구조는 목록이어야 합니다.")
        return [HealthRecord.from_dict(item) for item in data]

    @staticmethod
    def _records_from_txt_rows(rows: Any) -> list[HealthRecord]:
        """헤더가 없는 TXT 행을 HealthRecord 목록으로 변환합니다."""
        records = []
        for line_number, row in enumerate(rows, start=1):
            if not row:
                continue
            if len(row) != len(HealthRecord.FIELDS):
                raise ValueError(
                    f"TXT {line_number}행의 필드 수가 올바르지 않습니다."
                )
            data = dict(zip(HealthRecord.FIELDS, row))
            records.append(HealthRecord.from_dict(data))
        return records

    @staticmethod
    def _records_from_pickle(data: Any) -> list[HealthRecord]:
        """Pickle 객체 목록을 확인하고 HealthRecord 목록으로 변환합니다."""
        if not isinstance(data, list):
            raise ValueError("Pickle 데이터의 최상위 구조는 목록이어야 합니다.")
        records = []
        for item in data:
            if isinstance(item, HealthRecord):
                records.append(item)
            elif isinstance(item, dict):
                records.append(HealthRecord.from_dict(item))
            else:
                raise ValueError("Pickle 목록에는 레코드 객체만 들어갈 수 있습니다.")
        return records

    def save_json(self, path: str | Path | None = None) -> Path:
        """JSON 파일로 저장합니다."""
        return self.save("json", path)

    def load_json(self, path: str | Path | None = None) -> list[HealthRecord]:
        """JSON 파일을 불러옵니다."""
        return self.load("json", path)

    def save_csv(self, path: str | Path | None = None) -> Path:
        """CSV 파일로 저장합니다."""
        return self.save("csv", path)

    def load_csv(self, path: str | Path | None = None) -> list[HealthRecord]:
        """CSV 파일을 불러옵니다."""
        return self.load("csv", path)

    def save_txt(self, path: str | Path | None = None) -> Path:
        """TXT 파일로 저장합니다."""
        return self.save("txt", path)

    def load_txt(self, path: str | Path | None = None) -> list[HealthRecord]:
        """TXT 파일을 불러옵니다."""
        return self.load("txt", path)

    def save_pickle(self, path: str | Path | None = None) -> Path:
        """Pickle 파일로 저장합니다."""
        return self.save("pickle", path)

    def load_pickle(self, path: str | Path | None = None) -> list[HealthRecord]:
        """신뢰할 수 있는 Pickle 파일을 불러옵니다."""
        return self.load("pickle", path)

    def save_all(self) -> dict[str, Path]:
        """기본 데이터 폴더에 네 가지 형식으로 모두 저장합니다."""
        return {file_format: self.save(file_format) for file_format in self.FORMATS}


class StorageError(Exception):
    """건강정보 파일을 저장하거나 불러오는 중 발생한 오류입니다."""
