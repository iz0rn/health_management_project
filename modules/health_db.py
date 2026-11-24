"""건강정보 레코드와 파일 저장 기능을 제공합니다."""

# - 목적: 처음 배우는 학생도 이해하기 쉬운 코드로 health_db.py 정리
# - 프롬프트: "health_db.py 코드를 대학생 1년 수준으로 다시 만들어줘"
# - 사용자: 과제 제출자(이름 미제공)
# - 사용일: 2026-11-17

import csv
import json
import math
import pickle
from datetime import date
from pathlib import Path


class HealthRecord:
    """한 사람의 건강정보를 저장하는 클래스입니다."""

    FIELDS = [
        "id",
        "name",
        "birth_year",
        "gender",
        "height",
        "weight",
        "bmi",
        "status",
    ]

    def __init__(self, id, name, birth_year, gender, height, weight):
        """건강정보를 확인하고 BMI와 상태를 계산합니다."""
        if not isinstance(id, str) or not id.strip():
            raise ValueError("식별번호는 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("이름은 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(gender, str) or not gender.strip():
            raise ValueError("성별은 비어 있지 않은 문자열이어야 합니다.")
        if isinstance(birth_year, bool) or not isinstance(birth_year, int):
            raise ValueError("생년은 정수로 입력해야 합니다.")
        if birth_year <= 0:
            raise ValueError("생년은 0보다 커야 합니다.")

        self.id = id
        self.name = name.strip()
        self.birth_year = birth_year
        self.gender = gender.strip()
        self.height = self._positive_number(height, "키")
        self.weight = self._positive_number(weight, "몸무게")

        height_in_meters = self.height / 100
        self.bmi = round(self.weight / (height_in_meters * height_in_meters), 2)
        self.status = self._get_status()

    @staticmethod
    def _positive_number(value, label):
        """키나 몸무게가 0보다 큰 숫자인지 확인합니다."""
        if isinstance(value, bool):
            raise ValueError(label + "는 0보다 큰 숫자여야 합니다.")

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(label + "는 숫자로 입력해야 합니다.")

        if not math.isfinite(number) or number <= 0:
            raise ValueError(label + "는 0보다 큰 유한한 숫자여야 합니다.")

        return number

    def _get_status(self):
        """BMI 값에 맞는 건강 상태를 돌려줍니다."""
        if self.bmi < 18.5:
            return "저체중"
        if self.bmi < 23:
            return "정상"
        if self.bmi < 25:
            return "과체중"
        return "비만"

    def to_dict(self):
        """레코드 내용을 딕셔너리로 돌려줍니다."""
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
    def from_dict(cls, data):
        """딕셔너리의 내용을 사용해 레코드를 만듭니다."""
        required_fields = [
            "id",
            "name",
            "birth_year",
            "gender",
            "height",
            "weight",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError("필수 필드가 없습니다: " + field)

        birth_year = data["birth_year"]
        if isinstance(birth_year, bool):
            raise ValueError("생년은 정수로 입력해야 합니다.")

        try:
            parsed_birth_year = int(birth_year)
        except (TypeError, ValueError):
            raise ValueError("생년은 정수로 입력해야 합니다.")

        if isinstance(birth_year, float) and not birth_year.is_integer():
            raise ValueError("생년은 정수로 입력해야 합니다.")

        return cls(
            data["id"],
            data["name"],
            parsed_birth_year,
            data["gender"],
            data["height"],
            data["weight"],
        )


class HealthRecordManager:
    """건강정보 목록을 관리하고 파일에 저장합니다."""

    FORMATS = ["json", "csv", "txt", "pickle"]
    FILE_NAMES = {
        "json": "health_data.json",
        "csv": "health_data.csv",
        "txt": "health_data.txt",
        "pickle": "health_data.pkl",
    }

    def __init__(self, records=None, data_dir=None):
        """레코드 목록과 저장 폴더를 준비합니다."""
        if records is None:
            self.records = []
        else:
            self.records = list(records)

        for record in self.records:
            if not isinstance(record, HealthRecord):
                raise TypeError("records에는 HealthRecord 객체만 넣을 수 있습니다.")

        self._check_unique_ids(self.records)

        if data_dir is None:
            project_folder = Path(__file__).resolve().parent.parent
            self.data_dir = project_folder / "data"
        else:
            self.data_dir = Path(data_dir)

    @staticmethod
    def _check_unique_ids(records):
        """목록 안에 같은 식별번호가 있는지 확인합니다."""
        used_ids = []
        for record in records:
            if record.id in used_ids:
                raise ValueError("환자식별번호가 중복된 레코드가 있습니다.")
            used_ids.append(record.id)

    def _next_id(self):
        """올해 날짜를 기준으로 다음 식별번호를 만듭니다."""
        year = date.today().year
        prefix = "P" + str(year) + "-"
        largest_number = 0

        for record in self.records:
            if record.id.startswith(prefix):
                number_text = record.id[len(prefix):]
                if not number_text.isdigit():
                    continue
                try:
                    number = int(number_text)
                except ValueError:
                    continue

                if number > largest_number:
                    largest_number = number

        return prefix + str(largest_number + 1).zfill(4)

    def add_record(self, name, birth_year, gender, height, weight):
        """새 식별번호를 만든 뒤 레코드를 목록에 추가합니다."""
        record = HealthRecord(
            self._next_id(), name, birth_year, gender, height, weight
        )
        self.records.append(record)
        return record

    def display_records(self, records=None):
        """레코드 목록을 화면에 출력합니다."""
        if records is None:
            records = self.records

        print(" | ".join(HealthRecord.FIELDS))
        print("-" * len(" | ".join(HealthRecord.FIELDS)))

        if len(records) == 0:
            print("(등록된 건강정보가 없습니다.)")
            return

        for record in records:
            values = record.to_dict()
            row = []
            for field in HealthRecord.FIELDS:
                row.append(str(values[field]))
            print(" | ".join(row))

    def _get_file_path(self, file_format, path):
        """파일 형식을 확인하고 파일 경로를 돌려줍니다."""
        file_format = file_format.lower()

        if file_format not in self.FORMATS:
            formats = ", ".join(self.FORMATS)
            raise ValueError("지원하지 않는 파일 형식입니다. 지원 형식: " + formats)

        if path is not None:
            return Path(path)

        return self.data_dir / self.FILE_NAMES[file_format]

    def save(self, file_format, path=None):
        """레코드 목록을 지정한 파일 형식으로 저장합니다."""
        file_format = file_format.lower()
        file_path = self._get_file_path(file_format, path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if file_format == "pickle":
                with file_path.open("wb") as file:
                    pickle.dump(self.records, file)
            else:
                record_data = []
                for record in self.records:
                    record_data.append(record.to_dict())

                with file_path.open("w", encoding="utf-8", newline="") as file:
                    if file_format == "json":
                        json.dump(record_data, file, ensure_ascii=False, indent=2)
                        file.write("\n")
                    elif file_format == "csv":
                        writer = csv.DictWriter(
                            file, fieldnames=HealthRecord.FIELDS
                        )
                        writer.writeheader()
                        writer.writerows(record_data)
                    else:
                        writer = csv.writer(file)
                        for record in record_data:
                            row = []
                            for field in HealthRecord.FIELDS:
                                row.append(record[field])
                            writer.writerow(row)
        except (OSError, csv.Error, TypeError, pickle.PickleError) as error:
            raise StorageError(
                str(file_path) + " 저장에 실패했습니다: " + str(error)
            ) from error

        return file_path

    def load(self, file_format, path=None):
        """파일에서 레코드를 읽어 현재 목록을 바꿉니다."""
        file_format = file_format.lower()
        file_path = self._get_file_path(file_format, path)

        if not file_path.exists():
            self.records = []
            return self.records

        try:
            if file_format == "pickle":
                with file_path.open("rb") as file:
                    saved_data = pickle.load(file)
                records = self._records_from_pickle(saved_data)
            else:
                with file_path.open("r", encoding="utf-8", newline="") as file:
                    if file_format == "json":
                        saved_data = json.load(file)
                        records = self._records_from_dicts(saved_data)
                    elif file_format == "csv":
                        reader = csv.DictReader(file)
                        records = self._records_from_dicts(list(reader))
                    else:
                        reader = csv.reader(file)
                        records = self._records_from_txt_rows(reader)
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
            raise StorageError(
                str(file_path) + " 불러오기에 실패했습니다: " + str(error)
            ) from error

        self._check_unique_ids(records)
        self.records = records
        return self.records

    @staticmethod
    def _records_from_dicts(data):
        """딕셔너리 목록을 레코드 객체 목록으로 바꿉니다."""
        if not isinstance(data, list):
            raise ValueError("저장된 데이터는 목록이어야 합니다.")

        records = []
        for item in data:
            records.append(HealthRecord.from_dict(item))
        return records

    @staticmethod
    def _records_from_txt_rows(rows):
        """TXT 파일의 각 줄을 레코드 객체로 바꿉니다."""
        records = []

        for line_number, row in enumerate(rows, start=1):
            if len(row) == 0:
                continue
            if len(row) != len(HealthRecord.FIELDS):
                raise ValueError(
                    "TXT " + str(line_number) + "행의 필드 수가 올바르지 않습니다."
                )

            data = {}
            for index in range(len(HealthRecord.FIELDS)):
                field = HealthRecord.FIELDS[index]
                data[field] = row[index]
            records.append(HealthRecord.from_dict(data))

        return records

    @staticmethod
    def _records_from_pickle(data):
        """Pickle 파일의 내용을 레코드 객체 목록으로 바꿉니다."""
        if not isinstance(data, list):
            raise ValueError("Pickle 데이터는 목록이어야 합니다.")

        records = []
        for item in data:
            if isinstance(item, HealthRecord):
                records.append(item)
            elif isinstance(item, dict):
                records.append(HealthRecord.from_dict(item))
            else:
                raise ValueError("Pickle 목록에는 레코드만 들어갈 수 있습니다.")

        return records

    def save_json(self, path=None):
        """JSON 파일로 저장합니다."""
        return self.save("json", path)

    def load_json(self, path=None):
        """JSON 파일을 불러옵니다."""
        return self.load("json", path)

    def save_csv(self, path=None):
        """CSV 파일로 저장합니다."""
        return self.save("csv", path)

    def load_csv(self, path=None):
        """CSV 파일을 불러옵니다."""
        return self.load("csv", path)

    def save_txt(self, path=None):
        """TXT 파일로 저장합니다."""
        return self.save("txt", path)

    def load_txt(self, path=None):
        """TXT 파일을 불러옵니다."""
        return self.load("txt", path)

    def save_pickle(self, path=None):
        """Pickle 파일로 저장합니다."""
        return self.save("pickle", path)

    def load_pickle(self, path=None):
        """Pickle 파일을 불러옵니다."""
        return self.load("pickle", path)

    def save_all(self):
        """모든 형식으로 저장한 파일 경로를 돌려줍니다."""
        saved_paths = {}
        for file_format in self.FORMATS:
            saved_paths[file_format] = self.save(file_format)
        return saved_paths


class StorageError(Exception):
    """건강정보 파일을 저장하거나 불러올 때 발생하는 오류입니다."""
