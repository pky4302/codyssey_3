import time
import json

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
                analyze_json_data(data)

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
        
    score_a = measure_mac_time(pattern, filter_a)
    score_b = measure_mac_time(pattern, filter_b)

        
    result = classify_pattern(score_a, score_b)
        
    print("\n===== 판정 결과 =====")
    print("필터 A 점수:", score_a)
    print("필터 B 점수:", score_b)
    print("판정 결과:", result)
    print("필터 A 평균 연산 시간:", score_a, "ms")
    print("필터 B 평균 연산 시간:", score_b, "ms")


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

            
#MAC 연산
def mac_operation(pattern, filter):
    score = 0
    size = len(pattern)

    for i in range(size):
        for j in range(size):
            score += pattern[i][j] * filter[i][j]

    return score

#판정
def classify_pattern(score_a, score_b):
    epsilon = 1e-9

    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


#평균시간측정
def measure_mac_time(pattern, filter, repeat=10):
    start_time = time.perf_counter()

    for _ in range(repeat):
        mac_operation(pattern, filter)

    end_time = time.perf_counter()

    elapsed_time = (end_time - start_time) * 1000

    average_time = elapsed_time / repeat

    return average_time


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




#행렬사이즈 추출
def extract_size(pattern_key):
    parts = pattern_key.split("_")

    size = int(parts[1])

    return size


#json분석
def analyze_json_data(data):
    filters = data["filters"]
    patterns = data["patterns"]

    for pattern_key, pattern_data in patterns.items():

        #패턴이름에서 크기 추출
        size = extract_size(pattern_key)

        #크기에 맞는 필터 선택
        filter_key = f"size_{size}"
        selected_filter = filters[filter_key]

        #Cross와 X 핕터 가져오기
        cross_filter = selected_filter["cross"]
        x_filter = selected_filter["x"]

        #패턴 가져오기
        pattern = pattern_data["input"]

        #MAC 연산
        cross_score = mac_operation(pattern, cross_filter)
        x_score = mac_operation(pattern, x_filter)

        print("\n===== 분석 결과 =====")
        print("패턴 이름:", pattern_key)
        print("Cross 점수:", cross_score)
        print("X 점수:", x_score)


if __name__=="__main__":
    main()
