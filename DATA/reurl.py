import streamlit as st

# 리다이렉션 페이지에서 인증 코드 확인
def show_auth_code():
    # URL 파라미터에서 인증 코드 'code' 추출
    query_params = st.experimental_get_query_params()

    if 'code' in query_params:
        auth_code = query_params['code'][0]
        st.title("구글 인증 코드")
        st.write(f"인증 코드: {auth_code}")
        st.success("이 인증 코드를 사용하여 토큰을 발급받을 수 있습니다.")
    else:
        st.error("인증 코드가 없습니다. 다시 인증을 시도해주세요.")

# 페이지 표시
show_auth_code()
