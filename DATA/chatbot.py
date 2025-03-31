import streamlit as st
import pandas as pd
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread
import warnings
from datetime import datetime
from functions import map_city_to_two_letters,extract_and_remove_city,extract_and_remove_district,split_address, df_id, df_hang, mapping_city, mapping_districts, get_google_services,authenticate_google

# ✅ Streamlit UI 제목
st.title("💬 Data Auto system")

# ✅ 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "task" not in st.session_state:
    st.session_state.task = None
if "phone_string_column" not in st.session_state:
    st.session_state.phone_string_column = None
if "phone_target_column" not in st.session_state:
    st.session_state.phone_target_column = None
if "phone_file_uploaded" not in st.session_state:
    st.session_state.phone_file_uploaded = False
if "phone_df" not in st.session_state:
    st.session_state.phone_df = None
if "address_string_column" not in st.session_state:
    st.session_state.address_string_column = None
if "address_target_column" not in st.session_state:
    st.session_state.address_target_column = None
if "address_file_uploaded" not in st.session_state:
    st.session_state.address_file_uploaded = False
if "address_df" not in st.session_state:
    st.session_state.address_df = None
if "Negative_string_column" not in st.session_state:
    st.session_state.Negative_string_column = None
if "Negative_target_column" not in st.session_state:
    st.session_state.Negative_target_column = None
if "Negative_file_uploaded" not in st.session_state:
    st.session_state.Negative_file_uploaded = False
if "Negative_df" not in st.session_state:
    st.session_state.Negative_df = None

def reset_session():
    """세션을 초기화하는 함수"""
    st.session_state.task = None
    st.session_state.phone_string_column = None
    st.session_state.phone_target_column = None
    st.session_state.phone_file_uploaded = False
    st.session_state.phone_df = None  # 데이터프레임 초기화 추가
    st.session_state.address_string_column = None
    st.session_state.address_target_column = None
    st.session_state.address_file_uploaded = False
    st.session_state.address_df = None  # 데이터프레임 초기화 추가
    st.session_state.Negative_string_column = None
    st.session_state.Negative_target_column = None
    st.session_state.Negative_file_uploaded = False
    st.session_state.Negative_df = None  # 데이터프레임 초기화 추가
    st.session_state.messages = []

# ✅ 사이드바 명령어 안내
st.sidebar.title("📜 사용 가능 명령어")
if st.sidebar.button("🆕 새 채팅", key="new_chat_sidebar"):
    reset_session()
    st.rerun()


# ✅ 이전 대화 기록 표시 (채팅 UI)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ✅ 1. 작업 선택을 UI에서 클릭하여 선택
if st.session_state.task is None:
    selected_task = st.selectbox("💬 수행할 작업을 선택하세요:", ["", "중복 확인", "주소 정제","수신거부삭제"])

    if selected_task:
        st.session_state.task = selected_task
        st.session_state.messages.append({"role": "user", "content": f"📌 선택한 작업: {selected_task}"})

        if selected_task == "중복 확인":
            st.session_state.messages.append({"role": "assistant", "content": "🔤 문자열로 읽을 열을 입력해주세요. (예: '이름' 또는 '주소')"})
        elif selected_task == "주소 정제":
            st.session_state.messages.append({"role": "assistant", "content": "📍 주소 정제를 진행할 열을 입력해주세요!"})
        elif selected_task == "수신거부삭제":
            st.session_state.messages.append({"role": "assistant", "content": "📍 삭제를 진행할 열을 입력해주세요!"})
        st.rerun()  # 선택 즉시 리렌더링

#-------------------------------------------------------중복확인------------------------------------------------------------------------------------------------
# ✅ 2. phone 문자열로 읽을 열 선택
if st.session_state.task == "중복 확인" and st.session_state.phone_string_column is None:
    user_column = st.text_input("🔤 문자열로 읽을 열을 입력하세요...")
    if user_column:
        st.session_state.phone_string_column = user_column
        st.session_state.messages.append({"role": "user", "content": user_column})
        st.session_state.messages.append({"role": "assistant", "content": f"📂 '{user_column}' 열을 문자열로 변환합니다. 이제 파일을 업로드해주세요!"})
        st.rerun()

# ✅ 3. phone 파일 업로드
if st.session_state.phone_string_column and not st.session_state.phone_file_uploaded:
    upload_file = st.file_uploader("📂 CSV 또는 Excel 파일을 업로드하세요!", type=['csv', 'xlsx'])
    if upload_file is not None:
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file, dtype={st.session_state.phone_string_column: str}, low_memory=False)
        elif upload_file.name.endswith('.xlsx'):
            df = pd.read_excel(upload_file, dtype={st.session_state.phone_string_column: str})
        
        # ✅ 세션 상태 업데이트
        st.session_state.phone_df = df
        st.session_state.phone_file_uploaded = True
        st.session_state.messages.append({"role": "assistant", "content": "✅ 파일이 업로드되었습니다! 중복 확인할 열을 입력해주세요."})
        
        st.rerun()  # 🔄 리렌더링

# ✅ 4. phone 업로드된 파일 확인
if st.session_state.phone_df is not None:
    with st.chat_message("assistant"):
        st.write("📊 업로드된 데이터 미리보기:")
        st.dataframe(st.session_state.phone_df.head(5))  # 데이터프레임 상위 5개 행 출력
        
if st.session_state.phone_df is not None and st.session_state.phone_target_column is None:
    user_target_column = st.text_input("🔍 중복 확인할 열을 입력하세요...")

    if user_target_column:
        # ✅ 입력한 열이 데이터프레임에 존재하는지 확인
        if user_target_column not in st.session_state.phone_df.columns:
            st.warning(f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 다시 입력해주세요!")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 가능한 열: {', '.join(st.session_state.phone_df.columns)}"
            })
        else:
            st.session_state.phone_target_column = user_target_column
            st.session_state.messages.append({"role": "user", "content": user_target_column})
            st.session_state.messages.append({"role": "assistant", "content": f"⏳ '{user_target_column}' 열에서 중복을 확인 중입니다. 잠시만 기다려주세요!"})
            st.rerun()

# ✅ 5. 중복 확인 실행 및 결과 출력
if st.session_state.phone_df is not None and st.session_state.phone_target_column:
    df = st.session_state.phone_df.copy()
    df['중복_횟수'] = df[st.session_state.phone_target_column].map(df[st.session_state.phone_target_column].value_counts())
    df['등장_순서'] = df.groupby(st.session_state.phone_target_column).cumcount() + 1

    # ✅ 결과 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": "✅ 중복 확인이 완료되었습니다! 아래에서 결과를 확인하세요."})
    
    # ✅ 채팅 형식으로 출력
    with st.chat_message("assistant"):
        st.write(df)

    # ✅ CSV 다운로드 버튼 추가
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    csv_file.seek(0)

    st.download_button(
        label="📥 중복 확인 결과 다운로드",
        data=csv_file,
        file_name="중복_확인_결과.csv",
        mime="text/csv"
    )

    # ✅ 다시 시작 버튼 추가
    if st.button("🆕 새 채팅", key="new_chat_phone"):
        reset_session()
        st.rerun()

#----------------------------------------------------------주소정제---------------------------------------------------------------------------------------------
# ✅ 문자로 읽을 열이름 선택
if st.session_state.task == "주소 정제" and st.session_state.address_string_column is None:
    user_column = st.text_input("🔤 문자열로 읽을 열을 입력하세요...")
    if user_column:
        st.session_state.address_string_column = user_column
        st.session_state.messages.append({"role": "user", "content": user_column})
        st.session_state.messages.append({"role": "assistant", "content": f"📂 '{user_column}' 열을 문자열로 변환합니다. 이제 파일을 업로드해주세요!"})
        st.rerun()

# ✅ 2. address 파일 업로드
if st.session_state.address_string_column and not st.session_state.address_file_uploaded:
    upload_file = st.file_uploader("📂 CSV 또는 Excel 파일을 업로드하세요!", type=['csv', 'xlsx'])
    if upload_file is not None:
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file, dtype={st.session_state.address_string_column: str}, low_memory=False)
        elif upload_file.name.endswith('.xlsx'):
            df = pd.read_excel(upload_file, dtype={st.session_state.address_string_column: str})
        
        # ✅ 세션 상태 업데이트
        st.session_state.address_df = df
        st.session_state.address_file_uploaded = True
        st.session_state.messages.append({"role": "assistant", "content": "✅ 파일이 업로드되었습니다! 주소 정제를 시작할 열을 입력해주세요."})
        
        st.rerun()  # 🔄 리렌더링

# ✅ 4. address 업로드된 파일 확인
if st.session_state.address_df is not None:
    with st.chat_message("assistant"):
        st.write("📊 업로드된 데이터 미리보기:")
        st.dataframe(st.session_state.address_df.head())  # 데이터프레임 상위 5개 행 출력

# 5. 정제 할 열이름 입력
if st.session_state.address_df is not None and st.session_state.address_target_column is None:
    user_target_column = st.text_input("🔍 주소 나누기를 시작할 열을 입력하세요... 주소를 나눌필요 없다면 아래 '건너뛰기' 버튼을 눌러주세요")

    # "건너뛰기" 버튼 추가
    if st.button("🚶‍♂️ 건너뛰기"):
        st.session_state.address_target_column = "건너뛰기"
        st.session_state.messages.append({"role": "user", "content": "건너뛰기"})
        st.session_state.messages.append({"role": "assistant", "content": "⏳ 주소 정제를 건너뛰고 진행합니다."})
        st.rerun()

    # "건너뛰기" 외에 다른 열을 입력한 경우
    if user_target_column:
        if user_target_column not in st.session_state.address_df.columns:
            st.warning(f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 다시 입력해주세요!")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 가능한 열: {', '.join(st.session_state.address_df.columns)}"
            })
        else:
            st.session_state.address_target_column = user_target_column
            st.session_state.messages.append({"role": "user", "content": user_target_column})
            st.session_state.messages.append({"role": "assistant", "content": f"⏳ '{user_target_column}' 열에서 주소를 정제 중 입니다. 잠시만 기다려주세요!"})
            st.rerun()


#주소 정제 시작
if st.session_state.address_df is not None and st.session_state.address_target_column and st.session_state.address_target_column != "건너뛰기":
    df = st.session_state.address_df.copy()
    df['원본주소'] = df[st.session_state.address_target_column]
    df[st.session_state.address_target_column] = df[st.session_state.address_target_column].apply(map_city_to_two_letters)
    df[['시도', st.session_state.address_target_column]] = df[st.session_state.address_target_column].apply(lambda x: pd.Series(extract_and_remove_city(x)))
    df[['시군구', st.session_state.address_target_column]] = df[st.session_state.address_target_column].apply(lambda x: pd.Series(extract_and_remove_district(x)))
    df[['읍면동', st.session_state.address_target_column]] = df[st.session_state.address_target_column].apply(lambda x: pd.Series(split_address(x)))
    df.rename(columns={st.session_state.address_target_column: '세부주소'}, inplace=True)

    df['시도'] = df['시도'].str.replace(r'[^\w\s]', '', regex=True)
    df['시도'] = df['시도'].str.replace(r'\s+', '', regex=True)
    df['시군구'] = df['시군구'].astype(str).str.replace(r'\s+', '', regex=True)
    df['시군구'] = df['시군구'].str.replace(r'[^\w\s]', '', regex=True)
    df['시군구'] = df['시군구'].str.replace(r'\s+', '', regex=True)
    df['읍면동'] = df['읍면동'].str.replace(r'[^\w\s]', '', regex=True)
    df['읍면동'] = df['읍면동'].str.replace(r'\s+', '', regex=True)
    df['시도'].apply(mapping_city)
    df['시군구'].apply(mapping_districts)
    df = df.merge(df_hang, on=["시도", "시군구", "읍면동"], how="left")
    for index, row in df.iterrows():
    # Check if '행정동' is empty or NaN
        if pd.isna(row['행정동']) or row['행정동'].strip() == "":
            # Match '시도', '시군구', and '읍면동' from df to '시도', '시군구', '행정동' from df_hang
            match = df_hang[
                (df_hang['시도'] == row['시도']) & 
                (df_hang['시군구'] == row['시군구']) & 
                (df_hang['행정동'] == row['읍면동'])
            ]
            
            # If a match is found, update the '행정동' column in df
            if not match.empty:
                df.at[index, '행정동'] = match.iloc[0]['행정동']
    df["행정동"] = df["행정동"].fillna("F")
    df = df.merge(df_id, on=["시도", "시군구", "행정동"], how="left")
    df["ID"] = df["ID"].fillna("F")
    df = df[['원본주소', '시도', '시군구', '읍면동', '세부주소', '행정동', 'ID']]

    # ✅ 결과 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": "✅ 주소정제가 완료되었습니다! 아래에서 결과를 확인하세요."})
    
    # ✅ 채팅 형식으로 출력
    with st.chat_message("assistant"):
        st.write(df)

    # ✅ CSV 다운로드 버튼 추가
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    csv_file.seek(0)

    st.download_button(
        label="📥 주소 정제 결과 다운로드",
        data=csv_file,
        file_name="주소_정제_결과.csv",
        mime="text/csv"
    )

    # ✅ 다시 시작 버튼 추가
    if st.button("🆕 새 채팅", key="new_chat_phone"):
        reset_session()
        st.rerun()

#주소 정제 건너뛰기 선택 후 
if st.session_state.address_df is not None and st.session_state.address_target_column == "건너뛰기":
    df = st.session_state.address_df.copy()
    df['시도'] = df['시도'].str.replace(r'[^\w\s]', '', regex=True)
    df['시도'] = df['시도'].str.replace(r'\s+', '', regex=True)
    df['시군구'] = df['시군구'].astype(str).str.replace(r'\s+', '', regex=True)
    df['시군구'] = df['시군구'].str.replace(r'[^\w\s]', '', regex=True)
    df['시군구'] = df['시군구'].str.replace(r'\s+', '', regex=True)
    df['읍면동'] = df['읍면동'].str.replace(r'[^\w\s]', '', regex=True)
    df['읍면동'] = df['읍면동'].str.replace(r'\s+', '', regex=True)
    df['시도'] = df['시도'].apply(mapping_city)
    df['시군구'] = df['시군구'].apply(mapping_districts)

    df = df.merge(df_hang, on=["시도", "시군구", "읍면동"], how="left")
    for index, row in df.iterrows():
    # Check if '행정동' is empty or NaN
        if pd.isna(row['행정동']) or row['행정동'].strip() == "":
            # Match '시도', '시군구', and '읍면동' from df to '시도', '시군구', '행정동' from df_hang
            match = df_hang[
                (df_hang['시도'] == row['시도']) & 
                (df_hang['시군구'] == row['시군구']) & 
                (df_hang['행정동'] == row['읍면동'])
            ]
            
            # If a match is found, update the '행정동' column in df
            if not match.empty:
                df.at[index, '행정동'] = match.iloc[0]['행정동']
    df["행정동"] = df["행정동"].fillna("F")
    df = df.merge(df_id, on=["시도", "시군구", "행정동"], how="left")
    df["ID"] = df["ID"].fillna("F")
    df = df[['시도', '시군구', '읍면동', '세부주소', '행정동', 'ID']]

    # ✅ 결과 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": "✅ 주소정제가 완료되었습니다! 아래에서 결과를 확인하세요."})
    
    # ✅ 채팅 형식으로 출력
    with st.chat_message("assistant"):
        st.write(df)

    # ✅ CSV 다운로드 버튼 추가
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    csv_file.seek(0)

    st.download_button(
        label="📥 주소 정제 결과 다운로드",
        data=csv_file,
        file_name="주소_정제_결과.csv",
        mime="text/csv"
    )

    # ✅ 다시 시작 버튼 추가
    if st.button("🆕 새 채팅", key="new_chat_phone"):
        reset_session()
        st.rerun()

#----------------------------------------------------------080 ,자유마을,아웃콜 삭제요청---------------------------------------------------------------------------------------------# ✅ 문자로 읽을 열이름 선택
# ✅ 문자로 읽을 열이름 선택
if st.session_state.task == "수신거부삭제" and st.session_state.Negative_string_column is None:
    user_column = st.text_input("🔤 문자열로 읽을 열을 입력하세요...")
    if user_column:
        st.session_state.Negative_string_column = user_column
        st.session_state.messages.append({"role": "user", "content": user_column})
        st.session_state.messages.append({"role": "assistant", "content": f"📂 '{user_column}' 열을 문자열로 변환합니다. 삭제를 진행할 파일을 업로드해주세요!"})
        st.rerun()

# ✅ 2. Negative_df  파일 업로드
if st.session_state.Negative_string_column and not st.session_state.Negative_file_uploaded:
    upload_file = st.file_uploader("📂 CSV 또는 Excel 파일을 업로드하세요!", type=['csv', 'xlsx'])
    if upload_file is not None:
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file, dtype={st.session_state.Negative_string_column: str}, low_memory=False)
        elif upload_file.name.endswith('.xlsx'):
            df = pd.read_excel(upload_file, dtype={st.session_state.Negative_string_column: str})
        
        # ✅ 세션 상태 업데이트
        st.session_state.Negative_df = df
        st.session_state.Negative_file_uploaded = True
        st.session_state.messages.append({"role": "assistant", "content": "✅ 파일이 업로드되었습니다! 삭제를 시작할 열을 입력해주세요."})
        
        st.rerun()  # 🔄 리렌더링

# ✅ 4. Negative 업로드된 파일 확인
if st.session_state.Negative_df is not None:
    with st.chat_message("assistant"):
        st.write("📊 업로드된 데이터 미리보기:")
        st.dataframe(st.session_state.Negative_df.head())  # 데이터프레임 상위 5개 행 출력

if st.session_state.Negative_df is not None and st.session_state.Negative_target_column is None:
    user_target_column = st.text_input("🔍 제거를 진행할 열을 입력하세요...")

    if user_target_column:
        # ✅ 입력한 열이 데이터프레임에 존재하는지 확인
        if user_target_column not in st.session_state.Negative_df.columns:
            st.warning(f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 다시 입력해주세요!")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 가능한 열: {', '.join(st.session_state.Negative_df.columns)}"
            })
        else:
            st.session_state.Negative_target_column = user_target_column
            st.session_state.messages.append({"role": "user", "content": user_target_column})
            st.session_state.messages.append({"role": "assistant", "content": f"⏳ '{user_target_column}' 열에서 삭제를 진행 중입니다. 잠시만 기다려주세요!"})
            st.rerun()

# ✅ 5. 중복 제거 실행 및 결과 출력
if st.session_state.Negative_df is not None and st.session_state.Negative_target_column:
    df = st.session_state.Negative_df.copy()
    
    # Google 인증
    creds = authenticate_google()

    if creds is None:
        # 인증이 안 되었을 경우
        st.error("Google 인증이 필요합니다. 인증 후 다시 시도해주세요.")
        st.stop()

    gc, drive_service, sheets_service = get_google_services(creds)

    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

    current_year = datetime.now().year

    # Google Drive에서 최신 엑셀 파일 가져오기
    folder_id = '1NiTuONWRv7jWsqwmAzY0qEJkdls3__AO'
    exclude_sheets = ['드랍', '픽업', '자통당TM 구분']

    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
        spaces='drive',
        fields='files(id, name, createdTime)',
        orderBy='createdTime desc'
    ).execute()

    files = response.get('files', [])

    if not files:
        st.error("해당 폴더에 .xlsx 파일이 없습니다.")
    else:
        # 가장 최신 파일 다운로드
        latest_file = files[0]
        file_id = latest_file['id']
        file_name = latest_file['name']
        st.write(f"가장 최신 파일: {file_name}")

        request = drive_service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_stream.seek(0)

        # 모든 시트 읽기 (특정 시트 제외)
        excel_file = pd.ExcelFile(file_stream)
        sheets = [sheet for sheet in excel_file.sheet_names if sheet not in exclude_sheets]

        dtype_mapping = {
            '연락처': str,
            '고유값': str,
            '발신 전화번호': str,
            '픽업코드': str,
            '드랍코드': str,
            '결번': str,
            '부재중': str,
            '이미 가입': str,
            '가입 원함': str,
            '미온': str,
            '가입 거절': str,
            '삭제 요청': str,
            '타인': str,
            '투표 긍정': str,
            '다른 당 지지': str,
            '긍정': str,
            '번호변경': str
        }

        outcall_df = pd.concat(
            [excel_file.parse(sheet, dtype=dtype_mapping) for sheet in sheets],
            ignore_index=True
        )

        df = df[~df[st.session_state.Negative_target_column].isin(outcall_df['연락처'])]

        # ✅ 결과 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": "✅ 삭제가 완료되었습니다! 아래에서 결과를 확인하세요."})
        
        # ✅ 채팅 형식으로 출력
        with st.chat_message("assistant"):
            st.write(df)

        # ✅ CSV 다운로드 버튼 추가
        csv_file = io.BytesIO()
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        csv_file.seek(0)

        st.download_button(
            label="📥 중복 확인 결과 다운로드",
            data=csv_file,
            file_name="중복_확인_결과.csv",
            mime="text/csv"
        )

        # ✅ 다시 시작 버튼 추가
        if st.button("🆕 새 채팅", key="new_chat_phone"):
            reset_session()
            st.rerun()