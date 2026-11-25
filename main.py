"""간단한 건강정보 콘솔 프로그램입니다."""

# - 사용자: 김민재
# - 사용일: 2026-11-23

from modules.health_db import HealthRecordManager
from modules.health_logic import HealthManager


def print_records(records):
    """건강정보 목록을 출력합니다."""
    if len(records) == 0:
        print("등록된 건강정보가 없습니다.")
        return

    print("식별번호 | 이름 | 생년 | 성별 | 키 | 체중 | BMI | 상태")
    print("-" * 70)

    for record in records:
        print(
            record.id, "|",
            record.name, "|",
            record.birth_year, "|",
            record.gender, "|",
            record.height, "|",
            record.weight, "|",
            record.bmi, "|",
            record.status
        )


def input_number(text):
    """숫자를 입력받고, 잘못 입력하면 다시 입력받습니다."""
    while True:
        value = input(text)
        try:
            number = float(value)
            if number > 0:
                return number
            print("0보다 큰 숫자를 입력하세요.")
        except ValueError:
            print("숫자만 입력하세요.")


def main():
    db = HealthRecordManager()
    manager = HealthManager()

    # 시작할 때 JSON 파일을 읽어옵니다.
    records = db.load("json")
    for record in records:
        manager.add(record)

    while True:
        print("\n------ 건강정보 관리 시스템 ------")
        print("1. 건강정보 추가")
        print("2. 전체 목록 조회")
        print("3. 검색")
        print("4. 수정")
        print("5. 삭제")
        print("6. 통계 조회")
        print("7. 파일로 저장")
        print("0. 종료")

        menu = input("번호 선택: ")

        if menu == "1":
            name = input("이름: ")
            birth_year = int(input("생년: "))
            gender = input("성별(남/여): ")
            height = input_number("키(cm): ")
            weight = input_number("체중(kg): ")

            record = db.add_record(name, birth_year, gender, height, weight)
            manager.add(record)
            print("추가되었습니다.")

        elif menu == "2":
            print_records(manager.get_all())

        elif menu == "3":
            keyword = input("이름 또는 식별번호: ")
            result = manager.search(keyword)
            print_records(result)

        elif menu == "4":
            record_id = input("수정할 식별번호: ")

            record = manager.get_by_id(record_id)
            if record is None:
                print("레코드를 찾을 수 없습니다.")
            else:
                print("변경하지 않을 항목은 Enter를 누르세요.")

                name = input("이름: ")
                birth_year_text = input("생년: ")
                gender = input("성별(남/여): ")
                height_text = input("키(cm): ")
                weight_text = input("체중(kg): ")

                if name == "":
                    name = record.name
                if birth_year_text == "":
                    birth_year = record.birth_year
                else:
                    try:
                        birth_year = int(birth_year_text)
                    except ValueError:
                        print("생년은 정수로 입력하세요.")
                        continue
                if gender == "":
                    gender = record.gender
                if height_text == "":
                    height = record.height
                else:
                    try:
                        height = float(height_text)
                        if height <= 0:
                            print("키는 0보다 커야 합니다.")
                            continue
                    except ValueError:
                        print("키는 숫자로 입력하세요.")
                        continue
                if weight_text == "":
                    weight = record.weight
                else:
                    try:
                        weight = float(weight_text)
                        if weight <= 0:
                            print("체중은 0보다 커야 합니다.")
                            continue
                    except ValueError:
                        print("체중은 숫자로 입력하세요.")
                        continue

                manager.update(
                    record_id,
                    name,
                    birth_year,
                    gender,
                    height,
                    weight
                )
                print("수정되었습니다.")

        elif menu == "5":
            record_id = input("삭제할 식별번호: ")
            if manager.delete(record_id):
                print("삭제되었습니다.")
            else:
                print("레코드를 찾을 수 없습니다.")

        elif menu == "6":
            statistics = manager.get_statistics()
            print("\n=== 통계 ===")
            print("레코드 수:", statistics["count"])
            print("평균 키:", round(statistics["height_avg"], 2))
            print("키 표준편차:", round(statistics["height_std"], 2))
            print("평균 체중:", round(statistics["weight_avg"], 2))
            print("체중 표준편차:", round(statistics["weight_std"], 2))
            print("평균 BMI:", round(statistics["bmi_avg"], 2))
            print("BMI 표준편차:", round(statistics["bmi_std"], 2))

        elif menu == "7":
            db.records = manager.get_all()
            db.save("json")
            print("JSON 파일로 저장되었습니다.")

        elif menu == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 메뉴 번호입니다.")


if __name__ == "__main__":
    main()
