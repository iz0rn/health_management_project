"""건강정보를 메모리에서 관리하는 모듈입니다."""

# - 사용자: 김민재
# - 사용일: 2026-11-23

import math


class HealthManager:
    """HealthRecord 목록을 관리하는 간단한 클래스입니다."""

    def __init__(self):
        self.records = []

    def add(self, record):
        """새 건강정보를 추가합니다."""
        self.records.append(record)

    def get_all(self):
        """전체 건강정보 목록을 반환합니다."""
        return self.records

    def get_by_id(self, record_id):
        """식별번호로 건강정보를 찾습니다."""
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def search(self, keyword):
        """이름 또는 식별번호로 검색합니다."""
        result = []
        keyword = keyword.lower()

        for record in self.records:
            if keyword in record.name.lower() or keyword in record.id.lower():
                result.append(record)

        return result

    def update(self, record_id, name, birth_year, gender, height, weight):
        """건강정보를 수정합니다."""
        record = self.get_by_id(record_id)
        if record is None:
            return None

        record.name = name
        record.birth_year = birth_year
        record.gender = gender
        record.height = height
        record.weight = weight

        # 키와 체중이 바뀌면 BMI와 상태도 다시 계산합니다.
        record.bmi = round(weight / (height / 100) ** 2, 2)
        if record.bmi < 18.5:
            record.status = "저체중"
        elif record.bmi < 23:
            record.status = "정상"
        elif record.bmi < 25:
            record.status = "과체중"
        else:
            record.status = "비만"

        return record

    def delete(self, record_id):
        """식별번호로 건강정보를 삭제합니다."""
        record = self.get_by_id(record_id)
        if record is None:
            return False

        self.records.remove(record)
        return True

    def get_statistics(self):
        """레코드 수와 키, 체중, BMI의 평균을 계산합니다."""
        count = len(self.records)
        if count == 0:
            return {
                "count": 0,
                "height_avg": 0,
                "weight_avg": 0,
                "bmi_avg": 0,
                "height_std": 0,
                "weight_std": 0,
                "bmi_std": 0,
            }

        heights = []
        weights = []
        bmis = []

        for record in self.records:
            heights.append(record.height)
            weights.append(record.weight)
            bmis.append(record.bmi)

        height_avg = sum(heights) / count
        weight_avg = sum(weights) / count
        bmi_avg = sum(bmis) / count

        height_std = math.sqrt(
            sum((value - height_avg) ** 2 for value in heights) / count
        )
        weight_std = math.sqrt(
            sum((value - weight_avg) ** 2 for value in weights) / count
        )
        bmi_std = math.sqrt(
            sum((value - bmi_avg) ** 2 for value in bmis) / count
        )

        return {
            "count": count,
            "height_avg": height_avg,
            "weight_avg": weight_avg,
            "bmi_avg": bmi_avg,
            "height_std": height_std,
            "weight_std": weight_std,
            "bmi_std": bmi_std,
        }
