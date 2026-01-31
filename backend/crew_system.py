"""
CrewAI-based agent system. Uses CrewAI for orchestration.
- Serial: ingest -> planner -> reason -> respond -> guard
- Parallel: intent, memory, retrieve run concurrently after planner
- Async: memory save in BackgroundTasks (main.py)
"""
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.agents.ingestion import ingest
from backend.agents.planner import plan
from backend.agents.intent import classify
from backend.agents.retrieval import retrieve
from backend.agents.memory import load_memory
from backend.agents.reasoning import reason
from backend.agents.response import respond
from backend.agents.guardrails import guard


def _run_pipeline(ticket: str, task_id: str, timestamp: str) -> dict:
    """Run full agent pipeline. Called by CrewAI tool."""
    state = {"ticket": ticket, "input": ticket, "task_id": task_id, "timestamp": timestamp}

    state = ingest(state)
    state = plan(state)

    # Parallel: intent, memory, retrieve
    def run_intent():
        return ("intent", classify(dict(state)))
    def run_memory():
        return ("memory", load_memory(dict(state)))
    def run_retrieve():
        return ("retrieve", retrieve(dict(state)))

    merge_keys = ("priority", "action", "intent_details", "retrieved_docs", "context", "past_incidents",
                  "working_memory", "episodic_memory", "semantic_memory")
    with ThreadPoolExecutor(max_workers=3) as ex:
        for f in as_completed([ex.submit(run_intent), ex.submit(run_memory), ex.submit(run_retrieve)]):
            name, res = f.result()
            for k, v in res.items():
                if v is not None and k in merge_keys:
                    state[k] = v

    state = reason(state)
    state = respond(state)
    state = guard(state)
    return state


def invoke(inputs: dict) -> dict:
    """Entry point. Uses CrewAI when available, else direct pipeline with parallel execution."""
    ticket = inputs.get("ticket", inputs.get("input", ""))
    task_id = inputs.get("task_id", "default")
    timestamp = inputs.get("timestamp", datetime.now().isoformat())

    use_crewai = False
    try:
        from crewai import Agent, Task, Crew
        from crewai.tools import tool
        from backend import config
        use_crewai = True
    except ImportError:
        pass

    if use_crewai:
        try:
            @tool("Process support ticket through the agent pipeline")
            def process_ticket(ticket: str, task_id: str, timestamp: str) -> str:
                """Process ticket. Required: ticket, task_id, timestamp."""
                import json
                r = _run_pipeline(ticket, task_id, timestamp)
                return json.dumps({k: v for k, v in r.items() if v is not None}, default=str)

            from backend import config
            llm = None
            if not config.TEST_MODE and config.OPENAI_API_KEY:
                try:
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=config.OPENAI_API_KEY)
                except Exception:
                    pass

            agent = Agent(role="Support Orchestrator", goal="Process tickets via process_ticket tool",
                         backstory="You call process_ticket with ticket, task_id, timestamp.",
                         tools=[process_ticket], verbose=True, llm=llm)
            task = Task(description=f"Call process_ticket with ticket='{ticket[:150]}', task_id='{task_id}', timestamp='{timestamp}'",
                       expected_output="JSON with priority, action, response", agent=agent)
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            crew.kickoff(inputs={})

            import json
            out = str(task.output.raw) if task.output else "{}"
            state = json.loads(out) if out.strip().startswith("{") else {"response": out}
        except Exception as e:
            print(f"[CrewAI] Fallback to direct pipeline: {e}")
            state = _run_pipeline(ticket, task_id, timestamp)
    else:
        state = _run_pipeline(ticket, task_id, timestamp)

    state["task_id"] = task_id
    state["timestamp"] = timestamp
    state["ticket"] = ticket
    return state
