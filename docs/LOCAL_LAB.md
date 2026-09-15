# 로컬/클라우드 실험실 — 실행 가이드

## 무엇이 구현되어 있나

현재 버전은 `decomposion-eval 0.2.0.dev0`이며 명령어는 `decomposion`입니다.
PyPI에 게시된 릴리스가 아닙니다. 반드시 이 저장소의 체크아웃에서 설치하세요.
실험실은 **준비·격리·기록 도구**입니다. 코딩 에이전트, MCP 서버, 자동 추론 엔진을
구현했다고 주장하지 않습니다. CLI/CI 어느 쪽도 유료 모델을 자동 호출하지 않습니다.

Open WebUI는 지정된 커밋의 소스만 읽습니다. 서버 실행, Docker로 Open WebUI 배포,
모델 다운로드, GPU, Open WebUI의 Python/Node 의존성 설치는 필요하지 않습니다.

## 1. 설치와 확인

Git과 Python 3.11 이상이 필요합니다. 저장소 루트에서:

```bash
python3 scripts/bootstrap_lab.py
. .venv/bin/activate
decomposion --version
decomposion doctor
python -m pytest
decomposion check-suite
```

Windows에서는 `python scripts/bootstrap_lab.py` 실행 후
`.venv\Scripts\Activate.ps1`을 사용하세요. 같은 CLI는 Windows에서도 경로를 처리하지만,
이 PR의 CI 대상은 Linux/Python 3.11·3.13입니다. OS 전체 지원을 검증했다고 보지는 마세요.

bootstrap은 별도 venv를 만들고 이 체크아웃을 editable 설치합니다. 기존 비-venv 폴더나
symlink를 덮어쓰지 않습니다. 재설치는 같은 명령을 쓰되, 진행 중인 실험이 있다면
먼저 결과를 보존하세요. 자동 업데이트나 전역 Python 변경은 하지 않습니다.

## 2. 먼저 9회 smoke 실험 준비

```bash
export LAB="$HOME/decomposion-lab-smoke-v2"
decomposion lab init --workspace "$LAB" --profile smoke
```

이 명령은 GitHub에서 고정 커밋을 가져옵니다. 기본 브랜치를 추적하지 않습니다.
이미 해당 커밋의 깨끗한 로컬 clone이 있다면 네트워크 없이 준비할 수 있습니다:

```bash
decomposion lab init --workspace "$LAB" --profile smoke \
  --source-dir /absolute/path/to/pinned-open-webui
```

workspace는 **decomposion 저장소 밖**에 두세요. 기존 파일이 있는 미등록 폴더, 변경된
프로토콜, dirty checkout, 다른 커밋을 발견하면 중단하며 reset/clean하지 않습니다.

`smoke`는 P01·P02·P10 × 세 전략 × 1회 = 9개 세션,
`full`은 10개 프롬프트 × 세 전략 × 3회 = 90개 세션입니다.
실행 순서는 seed로 재현되는 무작위 순서입니다. 통계적 균형 배치를 보장하지는 않습니다.
`full`에는 별도 workspace를 쓰고 `--profile full`을 지정하세요.
초기에 90개의 checkout을 만들지 않고, start 때 해당 실행의 checkout만 생성합니다.

## 3. 첫 실행에 모델/에이전트 설정 고정

아래 MODEL은 실제로 선택한 **정확한 모델 ID**로 입력합니다. 임의의 예시 모델을
자동 선택하지 않습니다. Claude와 Codex 결과는 같은 실험 그룹으로 섞지 마세요.

```bash
export MODEL='사용할-정확한-모델-ID'
decomposion lab start --workspace "$LAB" --run P01-plain-r01 \
  --agent codex --agent-version "$(codex --version)" \
  --model "$MODEL" --thinking high --execution-environment local
```

이 명령은 에이전트를 실행하지 않습니다. `repo_path`, `request_path`를 출력합니다.
첫 실행의 설정은 저장되고 이후에는 재사용됩니다. 변경하려면 새 workspace를 만드세요.
모델/에이전트 정보는 사용자가 선언한 값이며 서버가 검증한 모델 정체성이 아닙니다.
`high`도 기록 필드입니다. 실제 에이전트에서 동일 설정을 적용해야 합니다.

이후에는 준비된 무작위 순서를 따를 수 있습니다:

```bash
decomposion lab status --workspace "$LAB"
decomposion lab start --workspace "$LAB"
```

## 4. 실제 모델 실행은 사용자 로컬에서

출력된 `repo_path`에서 새 세션을 열고 `request_path`의 **내용**을 입력하세요.
예를 들어 설치된 CLI가 지원하는 경우:

```bash
cd "$LAB/runs/P01-plain-r01/repo"
codex --sandbox read-only --model "$MODEL"
# 또는 별도 실험에서:
# claude --permission-mode plan --model "$MODEL"
```

정확한 플래그는 설치한 CLI의 `--help`로 확인하세요. 권한 우회 플래그는 쓰지 않습니다.
전역 메모리·MCP·플러그인·자동 로드되는 지침도 실험 오염원이므로 비활성화하거나
동일한 설정을 기록하세요. **별도 디렉터리는 보안 샌드박스가 아닙니다.**
엄격한 격리가 필요하면 실행별 VM/컨테이너에 그 실행의 repo와 request만 넣으세요.
다른 실행·golden 정답·개인 홈·운영 비밀키를 에이전트에 노출하지 마세요.

프롬프트에 조직/공유 같은 단어가 나와도 현재 코드에 그 개념이 이미 있다고 단정하지
않도록 되어 있습니다. 반대로 P10처럼 요구가 모호해도 코드에 증거가 있다면 unknown으로
숨겨서는 안 됩니다. 이미 구현된 기능을 다시 만들도록 계획하지 않는지도 확인하세요.

## 5. 원문 결과 기록

최종 답을 수정 없이 repo **밖**의 UTF-8 파일로 저장한 후:

```bash
cd /path/to/decomposion
decomposion lab record --workspace "$LAB" --run P01-plain-r01 \
  --stage 1 --answer /absolute/path/to/unedited-answer.md
```

plain/structured는 한 단계입니다. decomposion은 **4개의 실제 별도 단계**입니다:
현재 시스템/목표 → 영향 분석 → 누락·오류 비판 → 최종 작업/의존성 계획.
각 record 이후 생성된 다음 `request-XX.md`를 새 세션에 넣으세요. 그 입력에는
같은 실행의 앞선 결과만 포함됩니다. 마지막 단계만 제출하거나 다른 단계로 건너뛰면
거절합니다. 원문과 입력의 SHA-256, 단계 순서, 기록 시각을 보존합니다.

`--duration-seconds`는 사용자가 측정한 실행 시간만 넣으세요. 미입력 값은 unknown이며
0초/무료로 추정하지 않습니다. prepare와 record 사이 시간에는 사람이 기다린 시간이
포함되므로 모델 latency로 쓰지 않습니다. token/cost 자동 측정은 아직 구현되지 않았습니다.
재시도 시 같은 단계·같은 원문은 멱등 처리하며 다른 원문으로 덮어쓸 수 없습니다.

## 6. 상태와 검토

```bash
decomposion lab status --workspace "$LAB" > "$HOME/lab-status.json"
decomposion lab audit --workspace "$LAB"
```

`audit`는 입력·출력 해시와 단계 순서, 원본 checkout을 다시 검사합니다. 모든 해시를
함께 고치는 악의적 변조의 서명 검증은 아니며 의미상의 정답을 판정하지도 않습니다.

`recorded`는 원문이 기록되었다는 뜻이지 좋은 계획이라는 뜻이 아닙니다.
`quality_evaluated`는 false입니다. 이 10개는 어려운 **실험 프롬프트**이지 독립 검토를
거친 Golden 정답 10개가 아닙니다. 사람의 증거 검토 없이 우열/점수를 주장하지 마세요.

기존 `eval_harness.matrix_cli`는 고정 fixture를 통한 배선 테스트입니다. 실제 LLM 성능
실험과 분리됩니다. 기권 점수는 이제 `expected_abstentions`와 **실제** `abstentions`를
비교하며, 침묵이나 사실 주장과 기권을 동시에 하는 출력은 정답 처리하지 않습니다.
known-forbidden hit rate는 일반적인 precision/환각률과 다릅니다.

## 7. 버전·재현성

`experiment.lock.json`에 target SHA, manifest/prompt 원문 해시, 템플릿 전체, 실행 순서,
프로토콜 버전, Python/의존성/패키지 버전과 구현 소스 해시가 저장됩니다.
실험 중 구현이 달라지면 start/record가 중단됩니다. 원본 lock/답변을 수정하지 마세요.
Git tag는 자동 생성하지 않으며 PyPI 배포도 하지 않습니다. 재현 시 설치 저장소의 commit도
별도로 고정하고 보존하세요. OS/컨테이너 태그와 원격 모델 자체는 변경될 수 있으므로
같은 설정이 결과의 비트 단위 재현을 보장하지는 않습니다.

## 8. 클라우드와 CI

`.devcontainer/devcontainer.json`을 추가했습니다. Codespaces 또는 VS Code Dev Containers에서
열면 bootstrap으로 venv를 구성합니다. 클라우드에서도 LAB을 controller 밖에 두고,
`--execution-environment cloud`로 별도 실험을 만드세요. 인스턴스는 자동 생성하지 않습니다.
개발 컨테이너 이미지는 버전 태그이며 digest 고정은 아닙니다. 로컬 Docker가 없는 환경에서
컨테이너의 실제 기동 여부까지 검증했다고 주장하지 않습니다.

CI는 clean editable 설치, unit/regression tests, wheel 설치 후 외부 폴더 import,
실제 Open WebUI 고정 SHA clone/별도 실행 폴더 준비를 검증합니다. 모델을 호출하지 않으며
API 키나 운영 secrets가 필요하지 않습니다. GitHub Actions 로그가 통과하기 전에는
`mergeable`을 CI 성공으로 해석하지 마세요.

## 9. 개선 루프

실패를 발견하면 기존 실험을 수정하지 말고: 원문·증거 보존 → 최소 재현 테스트 추가 →
개발용 프롬프트/코드만 수정 → 새 버전/새 workspace로 비교 → 독립 검토를 진행합니다.
공개 저장소의 `blind` 이름만으로 비공개 holdout이 되지 않습니다. 검증 정답은 분석
에이전트가 접근하지 못하는 별도 위치에 보관하세요. C가 4단계이므로 A/B와 비교할 때
추가 연산량·사람 개입·시간도 함께 평가해야 합니다.

## 공식 참고 자료

- Python packaging: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- Codex CLI reference: https://developers.openai.com/codex/cli/reference/
- Claude Code permissions: https://code.claude.com/docs/en/permissions
- Dev Container specification: https://containers.dev/implementors/json_reference/
