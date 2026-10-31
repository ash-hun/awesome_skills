# 에이전트: LangGraph 구현 규칙

`dev_principle` 스킬의 참조 문서. LLM 에이전트나 워크플로를 만들 때 읽는다.

## 프레임워크

- 에이전트는 모두 LangGraph 로 구현한다. `StateGraph` 로 그래프를 만들고 `compile()` 한다.
- **Deepagents(`deepagents` 패키지)는 쓰지 않는다.** CrewAI, AutoGen, 직접 짠 while 루프 에이전트도 쓰지 않는다. 상태 저장, 중단 후 재개, 사람 승인을 그래프 밖에서 다시 만들게 된다.
- 단순한 도구 호출 에이전트면 직접 그래프를 짜기 전에 `langchain.agents.create_agent` 를 먼저 본다(사다리 3칸). LangGraph 그래프를 돌려주므로 checkpointer, `interrupt` 가 그대로 동작한다. `langgraph.prebuilt.create_react_agent` 는 LangGraph 1.x 에서 deprecated 이므로 새 코드에 쓰지 않는다. `ToolNode` 는 써도 된다.
- 모델 호출은 `langchain_core` 의 채팅 모델 인터페이스로 한다. 모델 이름과 버전은 설정에서 받고 고정한다.

## 디렉토리

에이전트는 `agent` 층에 둔다. 그래프 하나가 기능 하나다.

```
app/
├── agent/
│   ├── summary_graph.py       # 그래프 조립만. 노드 연결과 분기 조건
│   ├── summary_state.py       # 상태 모델
│   ├── summary_node.py        # 노드 구현. 노드가 많으면 역할별로 나눈다
│   └── summary_tool.py        # 이 그래프가 쓰는 도구
├── client/
│   └── llm_client.py          # 채팅 모델 생성과 설정
└── service/
    └── summary_service.py     # 그래프를 실행하고 결과를 업무 규칙에 맞게 다룬다
```

호출 방향은 다른 층과 같다. `api` 는 `service` 를 부르고, `service` 가 그래프를 실행한다. 그래프의 노드는 `repository`, `client` 를 부를 수 있지만 `api`, `service` 를 import 하지 않는다.

## 상태

- 상태는 `TypedDict` 나 pydantic 모델로 선언한다. 모든 필드에 타입을 쓴다.
- 메시지 목록처럼 누적되는 필드는 `Annotated[list[AnyMessage], add_messages]` 같은 reducer 로 선언한다. 노드가 목록 전체를 다시 쓰지 않는다.
- 상태에는 다음 노드가 판단에 쓰는 값만 넣는다. DB 세션, 클라이언트 객체, 비밀값을 상태에 넣지 않는다. checkpointer 가 상태를 저장하므로 그대로 디스크에 남는다.

## 노드

노드는 기능을 구현하는 atomic 모듈이다. 단위 테스트의 대상이 된다.

- 노드 하나는 결정 하나 또는 부수효과 하나를 맡는다. LLM 호출, 도구 실행, 결과 검증을 한 노드에 섞지 않는다.
- 노드는 상태를 받아 **바뀐 필드만** dict 로 돌려준다.
- LLM, 도구, 외부 클라이언트는 노드 클래스의 생성자로 주입한다. 테스트에서 mock 으로 바꾸려면 이 경로가 있어야 한다.

```python
class DraftNode:
    """요약 초안을 만드는 노드. summary_graph 가 조립하고 LLM 은 생성자로 받는다."""

    def __init__(self, model: BaseChatModel) -> None:
        self._model = model

    def __call__(self, state: SummaryState) -> dict[str, Any]:
        reply = self._model.invoke(build_draft_prompt(state["document"]))
        return {"draft": reply.content}
```

- 분기 함수(`add_conditional_edges` 의 조건)는 순수 함수로 쓴다. 상태만 읽고 다음 노드 이름을 돌려준다.
- LLM 출력은 다음 노드로 넘기기 전에 구조화 출력(`with_structured_output`)이나 pydantic 검증을 거친다.

## 실행과 멱등성

- 그래프 실행에는 항상 `config={"configurable": {"thread_id": ...}, "recursion_limit": N}` 을 넘긴다. `thread_id` 는 재실행해도 같은 값이 되는 자연 키(작업 ID, 대화 ID)로 고른다. 실행마다 새로 만든 `uuid4()` 를 쓰면 재개가 불가능하다.
- 중단 후 재개가 필요하면 checkpointer 를 붙인다. 운영은 영속 checkpointer(Postgres, SQLite), 테스트는 `InMemorySaver`.
- 같은 `thread_id` 로 다시 실행하면 마지막 체크포인트부터 이어진다는 사실을 `api_spec.md` 의 재호출 항목에 적는다.
- 되돌릴 수 없는 도구 호출 앞에는 `interrupt()` 로 사람 승인 노드를 둔다. 승인 후 `Command(resume=...)` 로 이어간다.
- 외부 부작용이 있는 노드는 재시도되어도 결과가 같아야 한다. 안 되면 `# idempotent:` 마커를 남긴다.

## 비용과 자원 (크리티컬 포인트)

- 실행마다 `recursion_limit`, LLM 호출 수, 토큰, 경과 시간에 상한을 둔다.
- 모델 호출에는 타임아웃과 재시도 상한을 건다.
- 반복 루프가 생기는 그래프(검증 실패 시 재작성 등)는 시도 횟수를 상태에 세고 상한에서 끝낸다.
- 동기 노드 안에서 블로킹 I/O 를 길게 하지 않는다. async 그래프면 노드도 async 로 쓴다.

보안 규칙(프롬프트 인젝션, 도구 최소 권한, 출력 검증)은 `references/security.md` 의 "LLM 과 에이전트" 절을 따른다.

## 테스트

`references/testing.md` 를 따르되 에이전트에 특화된 점만 적는다.

- **실제 LLM 을 부르지 않는다.** `langchain_core.language_models.fake_chat_models.GenericFakeChatModel` 이나 응답 목록을 돌려주는 대체 모델을 주입한다.
- 노드는 단위 테스트: `tests/unit/test_{기능명}_{노드모듈명}.py`. 가짜 모델의 응답을 정해 두고 노드가 돌려주는 상태 변경을 확인한다.
- 그래프는 통합 테스트: `tests/integ/test_{기능명}.py`. 가짜 모델과 mock 도구, `InMemorySaver` 로 그래프를 끝까지 실행하고 최종 상태와 분기 경로를 확인한다.
- 사람 승인 노드가 있으면 `interrupt` 에서 멈추는지와 `resume` 후 이어지는지를 한 시나리오로 확인한다.
