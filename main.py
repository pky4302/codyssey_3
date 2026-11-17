import time
import json
import copy


#메뉴
def show_menu():
    print("\n===== Mini NPU Simulator =====")
    print("1. 사용자 입력 모드")
    print("2. JSON 분석 모드")
    print("0. 프로그램 종료")

    choice = input("실행 모드를 선택하세요: ")

    return choice


#main
def main():
    while True:
        choice = show_menu()

        if choice == "1":
            user_input_mode()

        elif choice == "2":
            print("JSON 분석 모드를 실행합니다.")

            
            data = load_json_data()

            if data is not None:
                test_data = copy.deepcopy(data)
                
                test_data["patterns"]["size_5_2"]["input"][0][0] = "hello"
                
                analyze_json_data(test_data)
                performance_analysis()

        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 선택입니다. 다시 입력하세요.")



#사용자입력모드
def user_input_mode():
    print("\n===== 사용자 입력 모드 =====")

    while True:
        print("\n필터 A 입력")
        filter_a = input_matrix(3)
        
        print("\n필터 B 입력")
        filter_b = input_matrix(3)
        
        print("\n===== 입력한 필터 확인 =====")
        
        print("필터 A:")
        for row in filter_a:
            print(row)
        
        print("필터 B:")
        for row in filter_b:
            print(row)
        
        choice = input("\n입력한 필터가 맞습니까? (y/n): ").lower()
        
        if choice == "y":
            print("필터를 확정했습니다.")
            break
        
        elif choice == "n":
            print("필터를 다시 입력합니다.")

        else:
            print("y 또는 n을 입력하세요.")
        
    pattern = input_matrix(3)
    print("\n패턴 A 입력")

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
        
    average_a = measure_mac_time(pattern, filter_a)
    average_b = measure_mac_time(pattern, filter_b)

        
    result = classify_pattern(score_a, score_b)
        
    print("\n===== 판정 결과 =====")
    print("필터 A 점수:", score_a)
    print("필터 B 점수:", score_b)
    print("판정 결과:", result)
    print("필터 A 평균 연산 시간:", average_a, "ms")
    print("필터 B 평균 연산 시간:", average_b, "ms")

    performance_analysis()


#정사각형 행렬 입력받기
def input_matrix(size):
    matrix = []

    for i in range(size):
        while True:
            try:
                row = list(map(float, input(f"{i + 1}번째 행 입력: ").split()))
                
                if len(row) != size:
                    print(f"각 행에는 숫자 {size}개를 입력해야 합니다.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("숫자만 입력할 수 있습니다. 다시 입력하세요.")

    return matrix


#행렬크기검사
def validate_matrix(matrix, size):
    if not isinstance(matrix, list):
        return

    if len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list):
            return False

        if len(row) != size:
            return False

        for value in row:
            if not isinstance(value, (int, float)):
                return False

    return True

#행렬내부데이터검사
def validate_matrix_type(matrix):
    if not isinstance(matrix, list):
        return False, "행렬이 리스트 형식이 아닙니다."

    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            return False, f"{i + 1}번째 행이 리스트 형식이 아닙니다."

        for j, value in enumerate(row):
            if not isinstance(value, (int,float)):
                return False, (
                    f"{i + 1}행 {j + 1}열의 값이 숫자가 아닙니다. "
                    f"(입력값: {value!r})"
                )

    return True, None



#MAC 연산
def mac_operation(pattern, filter):
    score = 0
    size = len(pattern)

    for i in range(size):
        for j in range(size):
            score += pattern[i][j] * filter[i][j]

    return score


#성능분석용 테스트 행렬 생성
def create_test_matrix(size):
    matrix = []

    for i in range(size):
        row = []

        for j in range(size):
            row.append(1)

        matrix.append(row)

    return matrix

#평균시간측정
def measure_mac_time(pattern, filter, repeat=10):
    start_time = time.perf_counter()

    for _ in range(repeat):
        mac_operation(pattern, filter)

    end_time = time.perf_counter()

    elapsed_time = (end_time - start_time) * 1000

    average_time = elapsed_time / repeat

    return average_time


#판정
def classify_pattern(score_a, score_b):
    epsilon = 1e-9

    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


#json파일 불러오기
def load_json_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        print("JSON 파일을 성공적으로 읽었습니다.")

        return data

    except FileNotFoundError:
        print("data.json 파일을 찾을 수 없습니다.")
        return None

    except json.JSONDecodeError:
        print("JSON 파일 형식이 잘못되었습니다.")
        return None




#행렬사이즈 추출 및 예외검증
def extract_size(pattern_key):
    parts = pattern_key.split("_")

    if len(parts) != 3 or parts[0] != "size":
        raise ValueError("패턴 이름 형식 오류")

    size = int(parts[1])

    if size not in [5, 13, 25]:
        raise ValueError("지원하지 않는 행렬 크기")

    return size


#json분석
def analyze_json_data(data):
    pass_count = 0
    fail_count = 0
    fail_patterns = []
    fail_reasons = []

    filters = data["filters"]
    patterns = data["patterns"]

    for pattern_key, pattern_data in patterns.items():

        try:
            #패턴이름에서 크기 추출 (ex 5)
            size = extract_size(pattern_key)

        except ValueError as e:
            print(f"\n{pattern_key}: {e}")

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append(str(e))

            continue

        #크기에 맞는 필터 선택
        filter_key = f"size_{size}"

        if filter_key not in filters:
            print(f"\n{pattern_key}: {filter_key} 필터가 없습니다.")

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("해당 크기의 필터가 없음")

            continue

        selected_filter = filters[filter_key]


        if "cross" not in selected_filter or "x" not in selected_filter:
            print(f"\n{pattern_key}: 필터 항목이 누락되었습니다.")

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("cross 또는 x 항목 누락")

            continue

        if "input" not in pattern_data or "expected" not in pattern_data:
            print(f"\n{pattern_key}: 패턴 항목이 누락되었습니다.")
            
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("input 또는 expected 항목 누락")

            continue

        #Cross와 X 핕터 가져오기
        cross_filter = selected_filter["cross"]
        x_filter = selected_filter["x"]

        #패턴 가져오기
        pattern = pattern_data["input"]


        if not isinstance(pattern, list):
            print(f"\n{pattern_key}: 패턴 데이터 형이 잘못되었습니다.")

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("패턴 데이터가 리스트가 아님")

            continue

        if not isinstance(cross_filter, list):
            print(f"\n{pattern_key}: Cross 필터 데이터 형식이 잘못되었습니다.")

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("Cross 필터 데이터가 리스트가 아님")

            continue

        if not isinstance(x_filter, list):
            print(f"\n{pattern_key}: X 필터 데이터 형식이 잘못되었습니다.")
            
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("X 필터 데이터가 리스트가 아님")
            
            continue

               
        #행렬내부데이터검사
        is_valid, error_message = validate_matrix_type(cross_filter)
        
        if not is_valid:
            print(f"\n[FAIL] {pattern_key}")
            print("오류 위치: cross 필터")
            print("오류 내용:", error_message)
        
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append(error_message)
        
            continue

        is_valid, error_message = validate_matrix_type(cross_filter)
        
        if not is_valid:
            print(f"\n[FAIL] {pattern_key}")
            print("오류 위치: x 필터")
            print("오류 내용:", error_message)
        
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append(error_message)
        
            continue

        is_valid, error_message = validate_matrix_type(pattern)

        if not is_valid:
            print(f"\n[FAIL] {pattern_key}")
            print("오류 위치: input")
            print("오류 내용:", error_message)

            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append(error_message)

            continue

        #행렬 크기 검사
        if not validate_matrix(pattern, size):
            print(f"\n{pattern_key}: 패턴 크기가 잘못되었습니다.")
            status = "FAIL"
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("패턴 행렬 크기 오류")
            continue

        if not validate_matrix(cross_filter, size):
            print(f"\n{pattern_key}: Cross 필터 크기가 잘못되었습니다.")
            status = "FAIL"
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("Cross 필터 크기 오류")
            continue

        if not validate_matrix(x_filter, size):
            print(f"\n{pattern_key}: X 필터 크기가 잘못되었습니다.")
            status = "FAIL"
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("X 필터 크기 오류")
            continue

        #MAC 연산
        cross_score = mac_operation(pattern, cross_filter)
        x_score = mac_operation(pattern, x_filter)

        result = classify_pattern(cross_score, x_score)

        if result == "A":
            result = "Cross"
        elif result == "B":
            result = "X"

        expected = pattern_data["expected"]

        if expected == "+":
            expected = "Cross" #라벨 정규화
        elif expected == "x":
            expected = "X" #라벨 정규화

        if result == expected:
            status = "PASS"
            pass_count += 1
        else:
            status = "FAIL"
            fail_count += 1
            fail_patterns.append(pattern_key)
            fail_reasons.append("MAC 판정 결과와 정답 불일치")
        

        print("\n===== 분석 결과 =====")
        print("패턴 이름:", pattern_key)
        print("Cross 점수:", cross_score)
        print("X 점수:", x_score)
        print("판정결과:", result)
        print("정답:", expected)
        print("원본 정답:", repr(pattern_data["expected"]))
        print("테스트 결과:", status)

    #전체분석결과
    print("\n===== 전체 분석 결과 =====")
    print("전체 테스트:", pass_count + fail_count)
    print("PASS:", pass_count)
    print("FAIL:", fail_count)

    print("\n===== 실패 패턴 목록 =====")

    if fail_patterns:
        for i in range(len(fail_patterns)):
            print("패턴 이름:", fail_patterns[i])
            print("실패 원인:", fail_reasons[i])
    else:
        print("실패한 패턴이 없습니다.")


#성능테스트  
def performance_analysis():
    sizes = [3, 5, 13, 25]

    print("\n===== 성능 분석 =====")
    print("행렬 크기 | 평균 연산 시간(ms) | MAC 연산 수")

    for size in sizes:
        pattern = create_test_matrix(size)
        filter_matrix = create_test_matrix(size)

        average_time = measure_mac_time(pattern, filter_matrix)

        operation_count = size * size

        print(
            f"{size}x{size} | "
            f"{average_time:.6f}ms | "
            f"{operation_count}"
        )





if __name__=="__main__":
    main()
