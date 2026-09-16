# Planning Eval v1 요약

이 평가의 목적은 **AI가 만든 계획 자체의 품질**을 측정하는 것입니다. 그래프 UI가 보기 좋은지, 사람이 얼마나 빨리 리뷰하는지는 별도 평가로 분리합니다.

핵심 원칙:

- 정답은 하나의 고정 Task List가 아니라 반드시 만족해야 하는 **계획 제약 그래프**입니다.
- 중요한 누락은 `critical / major / minor`로 구분합니다.
- 문자열이 다르다고 오답으로 보지 않습니다.
- 새로운 발견은 자동으로 false positive 처리하지 않고 별도 검토 대상으로 둡니다.
- 모르는 사실을 말하지 않는 것과 명시적으로 `unknown`이라고 판단하는 것은 다릅니다. 침묵은 abstention이 아닙니다.
- 기계가 확실히 판단할 수 있는 구조 검사는 코드가, 의미적 동치성은 semantic layer가, 애매한 중요도·granularity·새로운 발견은 사람이 판정합니다.
- v1에서는 종합점수 하나를 만들지 않고 critical coverage, dependency, decision, risk, unsupported claim, uncertainty 등을 따로 봅니다.

Step 2에서는 이 계약으로 깊이 있는 Reference Case 3개만 먼저 작성하고, 표현이 안 되는 문제가 발견되면 10개로 확대하기 전에 schema를 수정합니다.
