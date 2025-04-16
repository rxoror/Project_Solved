## 문제 데이터 업데이트 모듈 ##
import requests  # HTTP 요청을 보내기 위한 라이브러리
import pandas as pd  # 데이터프레임 처리를 위한 pandas
import json  # JSON 파일 처리용 라이브러리
import numpy as np  # 수치 계산 및 배열 처리용 numpy
import time  # 시간 관련 기능을 위한 라이브러리
from concurrent.futures import ThreadPoolExecutor, as_completed  # 병렬 처리를 위한 라이브러리

# 문제 번호 목록을 받아 해당 백준 문제 정보를 일괄 조회하는 함수
def Problem_Lookup(problem_ids):
    url = "https://solved.ac/api/v3/problem/lookup"  # API URL
    headers = {"Accept": "application/json"}  # 요청 헤더 설정

    # 각 요청을 처리하는 함수 (50개씩 묶어서 요청)
    def fetch_batch(batch):
        params = {"problemIds": ",".join(batch.astype(str))}  # 요청할 문제 ID를 문자열로 변환
        response = requests.get(url, headers=headers, params=params)  # API 요청
        print(f"요청: {params['problemIds'][:10]}... → 상태 코드: {response.status_code}")  # 요청 상태 출력

        if response.status_code == 200:  # 요청 성공 시
            return response.json()  # JSON 응답 반환
        else:  # 요청 실패 시
            print(f"API 요청 실패, 상태 코드: {response.status_code}")  # 오류 메시지 출력
            return []  # 빈 리스트 반환

    # 문제 번호 배열로 만들고 50개씩 분할
    problem_ids = np.array(problem_ids)  # 문제 ID를 numpy 배열로 변환
    batch_size = 50  # 배치 크기 설정
    batches = [problem_ids[i:i + batch_size] for i in range(0, len(problem_ids), batch_size)]  # 배치 리스트 생성

    all_data = []  # 모든 문제 데이터를 저장할 리스트

    # 멀티스레드로 병렬 요청 처리
    with ThreadPoolExecutor(max_workers=10) as executor:  # 최대 10개의 스레드 사용
        futures = [executor.submit(fetch_batch, batch) for batch in batches]  # 각 배치에 대해 요청 제출
        for future in as_completed(futures):  # 모든 요청이 완료될 때까지 대기
            try:
                result = future.result()  # 결과 가져오기
                all_data.extend(result)  # 결과를 all_data에 추가
            except Exception as e:  # 오류 발생 시
                print(f"스레드 오류 발생: {e}")  # 오류 메시지 출력

    # JSON 파일로 저장
    with open("problems.json", "w", encoding="utf-8") as json_file:  # JSON 파일 열기
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)  # JSON 데이터 저장
    print("*** JSON 파일 저장 완료: problems.json")  # 저장 완료 메시지 출력

    # DataFrame으로 변환 후 CSV 저장
    df = pd.DataFrame(all_data)  # DataFrame 생성
    df.to_csv("problems.csv", index=False, encoding="utf-8-sig")  # CSV 파일로 저장
    print("*** CSV 파일 저장 완료: problems.csv")  # 저장 완료 메시지 출력

    return df  # DataFrame 반환

# 실행 영역

# 문제 번호 범위 지정 (1000 ~ 4999)
problem_ids = list(range(1000, 5000))  # 문제 ID 리스트 생성

def cvs_save():
    # 문제 정보 조회 및 DataFrame으로 반환
    df = Problem_Lookup(problem_ids)  # 문제 정보 조회 함수 호출

    # 주요 수치형 컬럼만 추출해서 저장
    numeric_df = df[['acceptedUserCount', 'level', 'votedUserCount', 'averageTries']]  # 필터링된 DataFrame 생성
    numeric_df.to_csv("filtered_problems.csv", index=False, encoding="utf-8-sig")  # 필터링된 데이터 CSV로 저장

# 결과 일부 출력
#print(df.head(3))  # 전체 데이터의 첫 3개 행 출력
#print(numeric_df.head(3))  # 필터링된 데이터의 첫 3개 행 출력

df = Problem_Lookup()