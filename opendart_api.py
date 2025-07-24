import requests

API_KEY = 'e3f8dfea848d383e1bc7f8af048616d0a7c22347'
BASE_URL = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyC0A_f8rL0dSV52RLt3F6YFio0yYGWClEU'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent'

# reprt_code 예시: 11011(사업보고서), 11012(반기), 11013(1분기), 11014(3분기)
def fetch_single_company_financials(corp_code, bsns_year, reprt_code):
    params = {
        'crtfc_key': API_KEY,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

def analyze_financials_with_gemini(financial_list, corp_name, bsns_year, reprt_name):
    """
    Gemini API를 활용해 재무 데이터를 쉽게 해석해주는 함수
    """
    # 주요 항목만 추출
    main_accounts = ['자산총계', '부채총계', '자본총계', '매출액', '영업이익', '당기순이익']
    filtered = [item for item in financial_list if item.get('account_nm') in main_accounts]
    # 요약용 텍스트 생성
    summary = f"회사명: {corp_name}\n연도: {bsns_year}\n보고서: {reprt_name}\n"
    for item in filtered:
        summary += f"{item['account_nm']}: 당기 {item.get('thstrm_amount','-')}, 전기 {item.get('frmtrm_amount','-')}, 전전기 {item.get('bfefrmtrm_amount','-')}\n"
    prompt = f"아래는 한국 상장사의 주요 재무 데이터입니다. 숫자를 쉽게 해석해주고, 비전문가도 이해할 수 있게 5문장 이내로 요약해줘.\n{summary}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    result = resp.json()
    # Gemini 응답 파싱
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return 'Gemini 요약 실패: ' + str(result)

if __name__ == '__main__':
    # 예시: 삼성전자 2018년 사업보고서
    data = fetch_single_company_financials('00126380', '2018', '11011')
    from pprint import pprint
    pprint(data)
    if data.get('status') == '000':
        print(analyze_financials_with_gemini(data['list'], '삼성전자', '2018', '사업보고서')) 