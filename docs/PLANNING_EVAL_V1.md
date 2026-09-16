# Planning Eval — small, evidence-backed development workbench

목적은 **좋은 계획을 만들고, 나중에 사람이 빠르고 정확하게 리뷰할 수 있게 하는 것**이다.
이번 범위는 계획 품질 평가다. UI, 코딩 에이전트 지휘, MCP 서버, 배포는 만들지 않는다.

## 다섯 단계와 실제 경계

| 단계 | 제공하는 것 | 이것만으로 증명되지 않는 것 |
|---|---|---|
| 1. 평가 계약 | 필수 고려사항, 중요도, 근거, 의존성, 불확실성 | 좋은 계획의 유일한 정답 |
| 2. 기준 사례 | 고정 Open WebUI 소스에 연결된 개발 사례 3개 | 독립 전문가가 검증한 Golden/Blind Set |
| 3. 평가기 검증 | 구조 검사, 리뷰 근거 검증, 통제된 오류 테스트 | 자연어 의미 판정의 정확도 |
| 4. 실험 구성 | 동일 근거 패킷, 4개 비교 방식, 제한된 실제 HTTP runner | 동일 계산량으로 비교했다는 주장 |
| 5. 실행·판단 | 명시적 모델 실행, 원문 보존, 선택적 LLM 리뷰, 결과 보고서 | 실행하지 않은 모델의 점수나 제품 우위 |

`planning-eval`은 개발용 도구다. `decomposion`의 기존 수동 실험실은 유지한다.
새 runner는 **고정된 코드 발췌를 모든 모델에 동일하게 주는 실험**이다.
전체 저장소를 자유 탐색하는 Codex/Claude Code 실험과는 다른 실험군이다. 결과를 섞지 않는다.

## 무엇을 측정하는가

Reference는 정답 Task 목록이 아니라 **충족해야 할 의무와 제약**이다.
각 obligation에는 `kind`, `severity`, `requirement`, `acceptance`, `basis`가 있다.
`basis`는 확인한 소스 ID 또는 명시된 변경 요구사항(`request`)을 가리킨다.

- `critical`: 누락/오류가 권한, 데이터, 핵심 동작을 크게 훼손할 수 있다.
- `major`: 중요한 영향·검토·운영 완결성을 놓친다.
- `minor`: 제한된 영향의 개선 사항이다. 현재 3개 사례에는 억지로 추가하지 않았다.

자동 검사와 의미 판정을 분리한다.

| 자동으로 확인하는 것 | 리뷰 판단이 필요한 것 |
|---|---|
| 중복 ID, 끊긴 edge, 잘못된 kind/state, hard cycle | 작업 내용이 실제 요구사항을 충족하는가 |
| 명시한 evidence ID가 패킷에 존재하는가 | 그 근거가 주장을 실제로 뒷받침하는가 |
| 리뷰의 case/plan 해시와 인용문이 일치하는가 | 인용문이 obligation을 의미적으로 만족하는가 |
| 리뷰에서 연결한 항목 간 선행 경로가 있는가 | 그 선행관계 자체가 타당한가 |
| task에 근거/추적 링크가 없는가 | 너무 잘게/크게 분해했는가 |

**인용문이 실제 존재한다는 검사는 그 판정이 옳다는 증명이 아니다.**
텍스트에 키워드가 있으면 정답으로 인정하는 matcher는 제거했다.
반대로 같은 단어가 없다는 이유로 누락이라고 자동 판정하지 않는다.

리뷰는 각 obligation을 `met / missing / contradicted / unresolved`로 판정한다.
`met`과 `contradicted`에는 실제 candidate node 인용문이 필요하다.
`missing`은 계획 전체를 검토한 리뷰어 판단이며, 침묵을 기권 성공으로 보상하지 않는다.
판정하지 않은 것은 `pending`이다. 미평가를 0점·만점·정확도로 바꾸지 않는다.

한 node가 여러 의무를 명시적으로 충족하거나 여러 node가 하나를 함께 충족해도 된다.
의존성은 `before -> after`의 **완료 수용 조건**이며 `precedes` 경로로 검사한다.
테스트를 먼저 작성하는 것을 금지하는 작업 순서가 아니다. 간접 선행 경로도 인정한다.
`informs / affects`의 cycle은 hard cycle이 아니다. 선이 없다고 무조건 병렬 가능하지도 않다.
의존 항목 자체가 누락됐으면 dependency 분모에서 제외하지 않는다.

새로운 제안은 `unadjudicated_nodes`에 남긴다. reference에 없다는 이유로 오답 처리하지 않는다.
과대/과소 분해, 잘못된 영향, 근거 없는 주장은 근거를 붙인 `plan_issues`로 별도 기록한다.
종합 점수, 승자, 임의 hard threshold는 없다. 구조가 잘못된 계획은 별도로 INVALID 표시한다.

## 근거 사례 3개

대상: `open-webui/open-webui`의 `0a7c15832fb30b1903753e83f81dc7d27e5b0944`.

| 사례 | 필수 항목 | 의존성 | 중요한 자기검토 수정 |
|---|---:|---:|---|
| P01 공유·회수 | 12 | 4 | 이미 존재하는 권한/공유 경로를 재사용·확장한다. 권한 하나 회수와 전체 접근 거부를 혼동하지 않는다. |
| P02 계정 삭제 | 12 | 4 | 기존 API는 관리자 전용이며 self-delete를 거부한다. 공유 자산·보존·부분 실패를 분리한다. |
| P10 감사 기능 | 12 | 3 | 감사 middleware가 이미 존재한다. 배포 설정·보존 기간·인증·tenant 구조는 코드 존재만으로 확정하지 않는다. |

모든 사례는 `development_unvalidated`다. 독립적인 정답 검증/일반화 주장을 하지 않는다.
각 소스의 commit, blob SHA, 줄 범위, anchor를 `prepare`가 실제 Git 내용과 대조한다.
발췌 밖의 구현이나 배포 설정은 모를 수 있다. 특히 '이 패킷에서 확인되지 않음'을
'전체 저장소에 없음'으로 바꾸면 안 된다. 세 사례에 없는 유효한 작업도 있을 수 있다.

## 설치 및 실제 실험

Git + Python 3.11 이상. 이 저장소의 **검증된 커밋을 체크아웃**한 뒤:

```bash
python3 scripts/bootstrap_lab.py
source .venv/bin/activate
planning-eval --version
planning-eval check
planning-eval selftest
python -m pytest
```

기존 실험실을 만들었다면 `$LAB/target`을 재사용한다. 없으면 새 경로에 준비한다.
Open WebUI 앱이나 그 의존성을 실행/설치하지 않는다.

```bash
export LAB="$HOME/decomposion-planning-source"
decomposion lab init --workspace "$LAB" --profile smoke

# 코드/근거/프롬프트를 고정한다. 기존 파일은 덮어쓰지 않는다.
planning-eval prepare --repo "$LAB/target" --out "$HOME/planning-packet.json"
cp experiments/planning-model.example.json "$HOME/planning-model.json"
```

`planning-model.json`의 endpoint와 model을 실제로 사용할 값으로 수정한다.
예제는 로컬의 **이미 실행 중인** OpenAI-compatible Chat Completions 서버를 가정한다.
CLI가 서버나 모델을 설치하거나 내려받지 않는다.

클라우드 API는 전체 HTTPS `/chat/completions` endpoint, 정확한 model ID,
`key_env`에 환경변수 **이름**을 설정한다. 키 값은 JSON/저장소에 넣지 않는다.
원격 HTTP는 거부한다. 사설 서버도 HTTPS 또는 SSH 터널의 loopback endpoint를 사용한다.
모델이 `max_tokens` 대신 `max_completion_tokens`를 요구하면 바꾸고,
지원하지 않는 `temperature` 등의 옵션은 제거한다. 해당 provider 문서를 따른다.

```bash
# 사전 계산만: API 키도 요청도 필요 없다. 결과 폴더도 만들지 않는다.
planning-eval run --packet "$HOME/planning-packet.json" \
  --config "$HOME/planning-model.json" --out "$HOME/planning-run-01" --max-calls 21

# 사용자가 실제 모델 호출을 시작하는 명령
planning-eval run --packet "$HOME/planning-packet.json" \
  --config "$HOME/planning-model.json" --out "$HOME/planning-run-01" --max-calls 21 --execute

planning-eval report --run "$HOME/planning-run-01" --out "$HOME/planning-report-01.md"
```

처음에는 3개 사례 × 4개 방식 × 1회 = **12개 계획 / 최대 21개 모델 요청**이다.
3회 반복은 `--repeats 3 --max-calls 63`으로 별도 폴더에서 실행한다.
이는 36개 계획/최대 63개 요청이다. `--strategies plain structured`처럼 좁힐 수도 있다.

| 방식 | 호출/계획 | 정의 |
|---|---:|---|
| plain | 1 | 직접 분석 요청 + 공통 근거/출력 계약 |
| structured | 1 | 관점을 명시한 강한 단일 프롬프트 |
| plan_solve | 1 | 문제를 나누고 해결해 합치는 공개 방법의 planning-only 변형 |
| decomposion | 4 | map → impact → critic → 최종 계획; 중간 원문을 다음 호출에 전달 |

Plan-and-Solve 변형은 원 논문의 실험 재현이나 별도 검증된 제품이 아니다.
동일 endpoint/model/options를 사용하지만, **Decomposion은 계산량이 더 많다**.
품질 상승이 나오더라도 계산량 증가만의 효과인지 분리하는 후속 대조 실험이 필요하다.
같은 model 문자열도 제공자의 내부 버전 고정을 보장하지 않는다. 응답 model/usage를 원문에 보존한다.
실행 순서는 고정 seed로 섞지만, 작은 샘플의 통계적 유의성을 주장하지 않는다.

출력 토큰 상한과 호출 수를 제한한다. 이것은 **달러 예산의 보장값이 아니다**.
입력 토큰/추론 토큰/가격 정책은 provider에 따라 다르다. 원문 usage가 있으면 보존하지만
가격을 임의 계산하지 않는다. 시간초과, 잘린 응답, JSON 실패 시 재시도하지 않고 중단한다.
이미 청구된 요청일 수 있으므로 새 실행을 하려면 기존 기록을 먼저 확인한다.

## 선택적 자동 리뷰와 결과 해석

리뷰 전 보고서의 semantic 항목은 pending이다. 사용자에게 수십 개의 기술적 승인 질문을
넘기는 대신, 별도 모델 설정으로 자동 리뷰를 실행할 수 있다. 같은 모델의 self-review에는
자기확증 위험이 있다. 다른 모델도 독립 전문가의 정답을 대신하지는 않는다.

```bash
# 설정은 planner와 같아도 되지만 독립 judge 설정 파일을 권장한다.
planning-eval judge --run "$HOME/planning-run-01" \
  --config "$HOME/planning-judge.json" --max-calls 12
planning-eval judge --run "$HOME/planning-run-01" \
  --config "$HOME/planning-judge.json" --max-calls 12 --execute
planning-eval report --run "$HOME/planning-run-01" --out "$HOME/planning-reviewed-01.md"
```

judge에는 계획의 strategy 이름을 주지 않는다. reference와 candidate 내용은 주므로
완벽한 blind가 아니며, 표현으로 strategy를 추정할 수도 있다. exact quote·hash·중복 판정을
검증하고 불명확하면 unresolved를 허용한다. **`judge_calibrated=false`**, 결과는 임시 판정이다.
전문가 확인 없이 자동으로 '검증된 성능' 또는 '일반화 성공'으로 승격하지 않는다.
새로운 발견/과소 분해 등도 reviewer의 설명과 후보 node를 함께 보존한다.

기록은 run.json, packet.json, trial별 입력/응답/최종 plan, review template, metadata,
summary.json으로 나뉜다. review.json은 별도 생성한다. 해시가 다른 과거 판정은 거부한다.
폴더/원문은 공개되지 않는다. 원격 provider를 쓰면 공급한 근거 코드가 전송된다.
공개 Open WebUI만 사용한 기본 실험과 달리 사내 소스를 넣기 전에는 전송 허용을 확인한다.

## 검증과 한계

CI는 기존 lab/fixture 평가를 유지하면서 다음을 확인한다.

- Linux Python 3.11/3.13의 설치, 전체 pytest, selftest.
- wheel을 별도 환경에 설치해 원본 폴더 밖에서 사례/CLI를 읽을 수 있는지.
- 실제 고정 Open WebUI 소스와 각 발췌의 blob/range/anchor를 확인하고 dry run.
- 로컬 Git fixture, 12계획/21호출 fake pipeline, 실제 HTTP client의 loopback mock,
  실패 보존, 호출 상한, 근거 누출 방지, 원문 변조 및 stale review 거부.

**Fixture/mock 통과는 실제 모델 품질 실험이 아니다.**
해시는 실수/변조 탐지를 돕지만 모든 해시를 같이 다시 쓸 수 있는 공격자를 막는 서명은 아니다.
유효한 evidence ID만으로 의미적 근거가 증명되지는 않는다. 전체 trace 의미와 과대/과소 분해는
리뷰 영역이다. 자동 model 선택, 자동 재개, MCP, DB, UI, 배포 계층을 추가하지 않았다.

### 자체 리뷰 기록

1. 이전 PR의 78-file 분산/중복 구조를 제거하고 core, experiment, CLI, selftest와 데이터로 통합.
2. 정확한 문자열 매칭을 semantic correctness로 오인하는 경로 제거; 미판정은 pending.
3. 누락된 endpoint가 dependency 분모에서 사라지는 문제 방지; hard/soft 관계 분리.
4. source 코드 주석과 구현이 다를 수 있음을 reference에 기록. 파일 접근권한의 direct-owner 검사,
   삭제 함수의 transaction 주석을 전체 원자성으로 일반화하지 않음.
5. API 키/유료 호출/외부 연결은 명시적 설정과 `--execute` 없이는 사용하지 않음.

개발 결과의 채택은 critical miss, 불필요한 확신, 미판정 수와 실제 원문을 함께 보고 결정한다.
현재 reference와 judge 신뢰도가 검증되기 전에는 종합 점수나 승자를 선언하지 않는다.

### 직접 참고한 1차 자료

- Plan-and-Solve Prompting: https://arxiv.org/abs/2305.04091
- Evaluation best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Chat Completions API: https://developers.openai.com/api/reference/resources/chat
- vLLM OpenAI-compatible server: https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/
