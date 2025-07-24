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