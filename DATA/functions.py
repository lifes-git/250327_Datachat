
import pandas as pd
import re

def split_address(address):
    if pd.isna(address):
        return "", address

    # 정규식을 사용하여 '문자+숫자+동' 만 추출
    eup_myeon_dong = re.findall(r'\b[가-힣]+[0-9]+[동]\b', address)

    # '읍면동'을 제외한 나머지 주소
    remaining_address = re.sub(r'\b[가-힣]+[0-9]+[동]\b', '', address).strip()

    # '읍면동'으로 끝나는 단어를 추출 (숫자 포함을 제외)
    eup_myeon_dong += re.findall(r'\b[가-힣]+[읍면동]\b(?![0-9])', remaining_address)

    # 추출한 단어들을 기존 주소에서 제거
    remaining_address = re.sub(r'\b[가-힣]+[읍면동]\b(?![0-9])', '', remaining_address).strip()

    # 추출한 단어를 쉼표로 연결하여 반환
    return ", ".join(eup_myeon_dong), remaining_address

city_list = [
    '강원', '강원도', '강원특별자치도', '경기', '경기도',
    '경남', '경상남도', '경북', '경상북도',
    '광주', '광주시', '광주광역시',
    '대구', '대구시', '대구광역시',
    '대전', '대전시', '대전광역시',
    '부산', '부산시', '부산광역시',
    '서울', '서울시', '서울특별시',
    '울산', '울산시', '울산광역시',
    '인천', '인천시', '인천광역시',
    '전남', '전라남도', '전북', '전라북도',
    '충남', '충청남도', '충북', '충청북도',
    '세종', '세종시', '세종특별자치시',
    '제주', '제주시', '제주특별자치도'
]

def extract_and_remove_city(address):
    # 주소가 None이거나 비어 있으면 그대로 반환
    if not address or pd.isna(address):
        return "", address

    # 시/도를 추출하고 나머지 주소에서 제거
    for city in city_list:
        if city in address:
            address = re.sub(city, '', address).strip()  # 시/도 삭제
            return city, address

    return "", address  # 시/도가 없는 경우

def extract_and_remove_district(address):
    if not address or pd.isna(address):
        return [], address

    # 모든 '시', '군', '구'를 찾아서 리스트로 추출
    districts = re.findall(r'\b\w+[시군구]\b', address)

    # 추출된 단어들을 주소에서 제거
    for district in districts:
        address = address.replace(district, '').strip()

    return districts, address

    return None, address  # '시군구'가 없을 경우

# 시/도를 두 글자로 줄이는 매핑 딕셔너리
city_mapping = {
    '강원도': '강원', '강원특별자치도': '강원',
    '경기도': '경기',
    '경상남도': '경남', '경남': '경남',
    '경상북도': '경북', '경북': '경북',
    '광주광역시': '광주', '광주시': '광주', '광주': '광주',
    '대구광역시': '대구', '대구시': '대구', '대구': '대구',
    '대전광역시': '대전', '대전시': '대전', '대전': '대전',
    '부산광역시': '부산', '부산시': '부산', '부산': '부산',
    '서울특별시': '서울', '서울시': '서울', '서울': '서울',
    '울산광역시': '울산', '울산시': '울산', '울산': '울산',
    '인천광역시': '인천', '인천시': '인천', '인천': '인천',
    '전라남도': '전남', '전남': '전남',
    '전라북도': '전북', '전북': '전북',
    '충청남도': '충남', '충남': '충남',
    '충청북도': '충북', '충북': '충북',
    '세종특별자치시': '세종', '세종시': '세종', '세종': '세종',
    '제주특별자치도': '제주', '제주시': '제주', '제주': '제주'
}

def map_city_to_two_letters(address):
    if not address or pd.isna(address):
        return address

    # 매핑 딕셔너리에서 모든 항목을 찾아서 두 글자 약어로 교체
    for full_name, short_name in city_mapping.items():
        address = re.sub(r'\b' + re.escape(full_name) + r'\b', short_name, address)

    return address

