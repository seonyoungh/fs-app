# 오픈다트 + Gemini AI 재무분석 서비스 배포 가이드 (Render)

## 1. 준비물
- Render.com 계정
- GitHub 저장소 (이 프로젝트 코드 push)
- 오픈다트 API Key, Gemini API Key

## 2. 코드 준비
- `requirements.txt`, `Procfile`가 포함되어 있어야 합니다.
- 민감한 API Key는 코드에 직접 쓰지 말고 Render 환경변수로 등록하세요.

## 3. 환경변수 설정 (Render Dashboard)
- `GEMINI_API_KEY` : Gemini API 키
- `DART_API_KEY` : 오픈다트 API 키

## 4. Render 배포 절차
1. [Render.com](https://render.com) 회원가입 및 로그인
2. New Web Service → GitHub 저장소 연결
3. Build Command: (비워두거나 기본값)
4. Start Command: `gunicorn app:app`
5. Python 버전 자동 감지 (필요시 `runtime.txt`에 명시)
6. 환경변수(GEMINI_API_KEY, DART_API_KEY) 등록
7. Deploy 클릭

## 5. 서비스 접속
- 배포 완료 후 Render가 제공하는 URL로 접속

## 6. 주의사항
- 무료 플랜은 슬립/재시작/트래픽 제한이 있습니다.
- API Key는 반드시 환경변수로 관리하세요.
- 오픈다트/Gemini API 일일 호출 제한에 유의하세요.

## 7. 기타
- 추가 기능/문의: GitHub Issue 또는 직접 문의 

아쉽게도, Render에 직접 코드를 업로드하거나 GitHub에 push하는 명령어는  
**사용자님의 컴퓨터에서 직접 실행**해야 합니다.  
(보안상 외부에서 GitHub 계정에 접근하거나 Render에 직접 업로드하는 것은 불가능합니다.)

하지만, 아래와 같이 **명령어와 절차**를 상세히 안내해드릴 수 있습니다!

---

## 1. GitHub에 코드 업로드(최초)

```bash
<code_block_to_apply_changes_from>
```

---

## 2. 코드 수정 후 업로드(이미 저장소가 있을 때)

```bash
git add .
git commit -m "Update: 내용"
git push
```

---

## 3. Render에서 GitHub 연동

1. [Render.com](https://render.com) → New Web Service → GitHub 저장소 선택
2. 환경변수 등록, Start Command 입력, Deploy

---

### 추가 안내
- GitHub 계정이 없다면 [회원가입](https://github.com/join) 후 새 저장소를 만드세요.
- 위 명령어에서 `https://github.com/본인계정/저장소이름.git` 부분은 본인 저장소 주소로 바꿔주세요.
- push 시 GitHub 계정/비밀번호 또는 토큰 입력이 필요할 수 있습니다.

---

**원하시면 위 명령어를 복사해서 터미널에 붙여넣기만 하면 됩니다!**  
추가로 궁금한 점이나 에러가 있으면 언제든 말씀해 주세요. 