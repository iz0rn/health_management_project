"""모듈 1의 레코드 입력, 4종 파일 저장 및 검증 실행 예제입니다."""

# AI 사용 기록
# - AI: OpenAI Copilot SDK
# - 목적: 모듈 1 동작을 보여 주고 파일 저장 후 원본과 비교 검증
# - 프롬프트: "첨부 지정프로젝트 요구사항에 따라 README를 읽고 모듈 1을 구현해줘."
# - 사용자: 과제 제출자(이름 미제공)
# - 사용일: 2026-11-16

from modules.health_db import HealthRecordManager


def main() -> None:
    """예제 레코드를 저장하고 네 가지 포맷의 복원 결과를 확인합니다."""
    manager = HealthRecordManager()
    manager.add_record("박민준", 1995, "남", 175.0, 72.5)
    manager.add_record("이서연", 1998, "여", 162.0, 52.0)
    manager.add_record("김도윤", 2001, "남", 180.0, 90.0)

    original_records = [record.to_dict() for record in manager.records]
    print("=== 저장 전 건강정보 ===")
    manager.display_records()

    saved_paths = manager.save_all()
    for file_format, path in saved_paths.items():
        verifier = HealthRecordManager(data_dir=manager.data_dir)
        loaded_records = verifier.load(file_format)
        loaded_values = [record.to_dict() for record in loaded_records]

        print(f"\n=== {file_format.upper()}에서 읽은 건강정보 ({path}) ===")
        verifier.display_records()
        if loaded_values != original_records:
            raise AssertionError(f"{file_format.upper()} 저장 데이터가 원본과 다릅니다.")
        print(f"{file_format.upper()} 검증 성공: 저장 전 데이터와 일치합니다.")


if __name__ == "__main__":
    main()