from llm.client import OllamaClient
from llm.generation import generate_validated
from llm.prompts import SCENARIO_PROMPT_TEMPLATE, SCENARIO_RETRY_SUFFIX
from llm.schemas import ScenarioPayload


def generate_scenario(client: OllamaClient, topic: str, difficulty: str) -> ScenarioPayload | None:
    result = generate_validated(
        client=client,
        prompt_template=SCENARIO_PROMPT_TEMPLATE,
        retry_suffix=SCENARIO_RETRY_SUFFIX,
        payload_cls=ScenarioPayload,
        topic=topic,
        difficulty=difficulty,
        log_context=f"scenario topic={topic} difficulty={difficulty}",
    )
    return result  # type: ignore[return-value]


def generate_scenario_batch(
    client: OllamaClient, topic: str, difficulty: str, count: int
) -> list[ScenarioPayload]:
    results: list[ScenarioPayload] = []
    for _ in range(count):
        scenario = generate_scenario(client, topic, difficulty)
        if scenario is not None:
            results.append(scenario)
    return results
