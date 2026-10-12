# ChargeOps ChatOps + Alert Router + CSMS Mock Lab

## 전체 흐름

`ChatOps Bot (demo_emit) → Alert Router → Slack #ops-alerts → Socket Mode → ChatOps Bolt → CSMS Mock`

실제 CSMS가 없으므로 CSMS Mock API가 Incident를 등록하고 상태를 PENDING → APPROVED로 변경합니다. 테스트 승인 시 장비 동작, Pod 재시작 등의 실제 위험 작업은 수행하지 않습니다.

## 시작하기

1. Slack에서 채널 `ops-alerts`를 생성하고 Slack App을 만들어 Socket Mode를 켜세요. App-level token에 `connections:write`, Bot Token에 `chat:write`를 추가하고 앱을 설치한 뒤 채널에 초대하세요. Interactivity도 활성화하세요.
2. `config/.env.example`을 `config/.env`로 복사하고 값을 채우세요. Slack Bot Token은 `xoxb-`, App-level Token은 `xapp-`로 시작합니다. 승인자 ID는 `U...` 형식입니다.
3. 가상환경 설정: `python -m venv .venv`, 활성화한 후 `pip install -r requirements-dev.txt`.
4. `python scripts/check_slack.py`로 Slack 연결을 확인하세요. Team ID는 이 명령으로 검증할 수 있습니다.
5. `python -m pytest -q`
6. `docker login`; `docker build -t DOCKERHUB_ID/chatops-csms-lab:v1 .`; `docker push DOCKERHUB_ID/chatops-csms-lab:v1`
7. `kubectl apply -f k8s/01-namespace.yaml`
8. `python scripts/setup_k8s.py`
9. `python scripts/render_manifest.py --image DOCKERHUB_ID/chatops-csms-lab:v1`
10. `kubectl apply -f k8s/rendered.yaml`
11. `kubectl -n chargeops get deploy,pod,svc`
12. `kubectl -n chargeops exec deploy/chatops-bot -- python -m app.demo_emit`
13. Slack `#ops-alerts`에서 `조회` → `승인` 클릭 후 로그 확인.

상세 UI 단계, Windows PowerShell 명령, 진단표는 함께 제공되는 HTML 가이드를 참고하세요.

## 참고
- 이미지 Public 권장(학습용). Private인 경우 imagePullSecrets를 생성해 Pod spec에 설정해야 합니다.
- 현재 DB는 Kubernetes `emptyDir`에 저장되므로 mock-csms Pod 재생성 시 데이터가 소실됩니다.
- `bot-backend-credentials` Secret의 내부 토큰은 backend 호출 인증용이고 Slack 토큰이 아닙니다.
- 프로덕션은 DB/PVC, 재시도 큐, 감사 기록, 승인 만료, 정책 게이트와 승인자 인증을 강화해야 합니다.
- `kubectl -n chargeops exec deploy/chatops-bot -- python -m app.demo_verify INCIDENT_ID` 로 CSMS Mock 승인 상태와 감사 로그를 조회할 수 있습니다.
