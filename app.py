from flask import Flask, request, render_template_string, redirect, url_for, send_file
import sqlite3
import opendart_api
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 서버에서 GUI 없이 사용
from opendart_api import analyze_financials_with_gemini, fetch_single_company_financials

app = Flask(__name__)
DB_FILE = 'corp.db'

SEARCH_FORM = '''
<!doctype html>
<title>회사명으로 corp_code 검색</title>
<h2>회사명으로 corp_code 검색</h2>
<form method="get">
  <input type="text" name="corp_name" placeholder="회사명 입력" required value="{{ request.args.get('corp_name', '') }}">
  <input type="submit" value="검색">
</form>
{% if results is not none %}
  <h3>검색 결과</h3>
  {% if results %}
    <table border="1" cellpadding="5">
      <tr><th>회사명</th><th>corp_code</th><th>stock_code</th><th>modify_date</th><th>재무조회</th></tr>
      {% for row in results %}
        <tr>
          <td>{{ row[1] }}</td>
          <td>{{ row[0] }}</td>
          <td>{{ row[2] }}</td>
          <td>{{ row[3] }}</td>
          <td>
            <form action="{{ url_for('financial_query') }}" method="get" style="margin:0;">
              <input type="hidden" name="corp_code" value="{{ row[0] }}">
              <input type="hidden" name="corp_name" value="{{ row[1] }}">
              <input type="submit" value="재무조회">
            </form>
          </td>
        </tr>
      {% endfor %}
    </table>
  {% else %}
    <p>검색 결과가 없습니다.</p>
  {% endif %}
{% endif %}
'''

FINANCIAL_FORM = '''
<!doctype html>
<title>재무정보 조회</title>
<h2>{{ corp_name }} ({{ corp_code }}) 재무정보 조회</h2>
<form method="post">
  <label>사업연도: <input type="text" name="bsns_year" value="{{ bsns_year or '' }}" required placeholder="예: 2023"></label>
  <label>보고서코드:
    <select name="reprt_code">
      <option value="11011" {% if reprt_code=='11011' %}selected{% endif %}>사업보고서(11011)</option>
      <option value="11012" {% if reprt_code=='11012' %}selected{% endif %}>반기보고서(11012)</option>
      <option value="11013" {% if reprt_code=='11013' %}selected{% endif %}>1분기보고서(11013)</option>
      <option value="11014" {% if reprt_code=='11014' %}selected{% endif %}>3분기보고서(11014)</option>
    </select>
  </label>
  <input type="hidden" name="corp_code" value="{{ corp_code }}">
  <input type="hidden" name="corp_name" value="{{ corp_name }}">
  <input type="submit" value="조회">
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
{% if data %}
  <h3>재무 데이터</h3>
  <table border="1" cellpadding="5">
    <tr>
      <th>계정명</th><th>당기금액</th><th>전기금액</th><th>전전기금액</th><th>재무제표명</th><th>재무제표구분</th><th>재무제표명(한글)</th>
    </tr>
    {% for item in data %}
      <tr>
        <td>{{ item['account_nm'] }}</td>
        <td>{{ item.get('thstrm_amount', '-') }}</td>
        <td>{{ item.get('frmtrm_amount', '-') }}</td>
        <td>{{ item.get('bfefrmtrm_amount', '-') }}</td>
        <td>{{ item.get('fs_nm', '-') }}</td>
        <td>{{ item.get('sj_div', '-') }}</td>
        <td>{{ item.get('sj_nm', '-') }}</td>
      </tr>
    {% endfor %}
  </table>
  <form method="post">
    <input type="hidden" name="corp_code" value="{{ corp_code }}">
    <input type="hidden" name="corp_name" value="{{ corp_name }}">
    <input type="hidden" name="bsns_year" value="{{ bsns_year }}">
    <input type="hidden" name="reprt_code" value="{{ reprt_code }}">
    <input type="hidden" name="ai_analyze" value="1">
    <input type="submit" value="AI 분석">
  </form>
  <h3>주요 항목 그래프</h3>
  <img src="{{ url_for('financial_chart', corp_code=corp_code, bsns_year=bsns_year, reprt_code=reprt_code) }}" alt="재무 그래프">
{% endif %}
{% if gemini_summary %}
  <div style="background:#f8f8e8; border:1px solid #ccc; padding:10px; margin:10px 0; font-size:1.1em;">
    <b>Gemini AI 분석:</b><br>{{ gemini_summary|safe }}
  </div>
{% endif %}
<a href="/">← 회사 검색으로 돌아가기</a>
'''

@app.route('/', methods=['GET'])
def search():
    corp_name = request.args.get('corp_name', '')
    results = None
    if corp_name:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT corp_code, corp_name, stock_code, modify_date
            FROM corp
            WHERE corp_name LIKE ?
            ORDER BY corp_name
        """, (f'%{corp_name}%',))
        results = c.fetchall()
        conn.close()
    return render_template_string(SEARCH_FORM, results=results)

@app.route('/financial', methods=['GET', 'POST'])
def financial_query():
    corp_code = request.values.get('corp_code')
    corp_name = request.values.get('corp_name')
    bsns_year = None
    reprt_code = '11011'
    error = None
    data = None
    gemini_summary = None
    reprt_name_map = {'11011': '사업보고서', '11012': '반기보고서', '11013': '1분기보고서', '11014': '3분기보고서'}
    ai_analyze = False
    prev_data = None
    if request.method == 'POST':
        bsns_year = request.form.get('bsns_year')
        reprt_code = request.form.get('reprt_code')
        ai_analyze = request.form.get('ai_analyze') == '1'
        try:
            api_result = fetch_single_company_financials(corp_code, bsns_year, reprt_code)
            if api_result.get('status') == '000':
                data = api_result.get('list', [])
                if not data:
                    error = '데이터가 없습니다.'
                else:
                    # 전년도 데이터도 불러오기
                    prev_year = str(int(bsns_year)-1) if bsns_year and bsns_year.isdigit() else None
                    if ai_analyze and prev_year:
                        prev_result = fetch_single_company_financials(corp_code, prev_year, reprt_code)
                        if prev_result.get('status') == '000':
                            prev_data = prev_result.get('list', [])
                        else:
                            prev_data = None
                        gemini_summary = analyze_financials_with_gemini(
                            data,
                            corp_name,
                            bsns_year,
                            reprt_name_map.get(reprt_code, reprt_code)
                        )
                        # 전년도 데이터도 함께 전달
                        if prev_data:
                            gemini_summary += '\n\n[전년도 주요 데이터]\n'
                            main_accounts = ['자산총계', '부채총계', '자본총계', '매출액', '영업이익', '당기순이익']
                            for item in prev_data:
                                if item.get('account_nm') in main_accounts:
                                    gemini_summary += f"{item['account_nm']} (전년도): 당기 {item.get('thstrm_amount','-')}, 전기 {item.get('frmtrm_amount','-')}, 전전기 {item.get('bfefrmtrm_amount','-')}\n"
            else:
                error = f"API 오류: {api_result.get('message')}"
        except Exception as e:
            error = f"API 호출 실패: {e}"
    return render_template_string(FINANCIAL_FORM, corp_code=corp_code, corp_name=corp_name, bsns_year=bsns_year, reprt_code=reprt_code, data=data, error=error, gemini_summary=gemini_summary)

@app.route('/financial_chart')
def financial_chart():
    corp_code = request.args.get('corp_code')
    bsns_year = request.args.get('bsns_year')
    reprt_code = request.args.get('reprt_code', '11011')
    api_result = fetch_single_company_financials(corp_code, bsns_year, reprt_code)
    data = api_result.get('list', []) if api_result.get('status') == '000' else []
    # 주요 항목만 추출
    main_accounts = ['자산총계', '부채총계', '자본총계', '매출액', '영업이익', '당기순이익']
    items = [item for item in data if item.get('account_nm') in main_accounts]
    labels = [item['account_nm'] for item in items]
    thstrm = [parse_amount(item.get('thstrm_amount')) for item in items]
    frmtrm = [parse_amount(item.get('frmtrm_amount')) for item in items]
    bfefrmtrm = [parse_amount(item.get('bfefrmtrm_amount')) for item in items]
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(labels))
    width = 0.25
    bars1 = ax.bar([i-width for i in x], thstrm, width, label='당기')
    bars2 = ax.bar(x, frmtrm, width, label='전기')
    bars3 = ax.bar([i+width for i in x], bfefrmtrm, width, label='전전기')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontproperties="AppleGothic" if matplotlib.get_backend() == 'MacOSX' else None)
    ax.set_ylabel('금액(원)')
    ax.set_title('주요 재무 항목 비교')
    ax.legend()
    # 각 바 위에 수치 표시
    def autolabel(bars, values):
        for bar, val in zip(bars, values):
            ax.annotate(f'{val:,}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, rotation=90)
    autolabel(bars1, thstrm)
    autolabel(bars2, frmtrm)
    autolabel(bars3, bfefrmtrm)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def parse_amount(val):
    if not val or val == '-':
        return 0
    return int(val.replace(',', ''))

if __name__ == '__main__':
    app.run(debug=True) 