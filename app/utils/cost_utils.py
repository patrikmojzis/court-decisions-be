from typing import TYPE_CHECKING

from google.genai.types import GenerateContentResponseUsageMetadata
from openai.types import CompletionUsage

from app.config.costs import llm_costs

if TYPE_CHECKING:
    from app.models.episode_model import Episode


def calculate_llm_costs(usage: CompletionUsage | GenerateContentResponseUsageMetadata, model = "gpt-4o-mini-2024-07-18") -> float:
    """
    Calculate the cost of an OpenAI API call based on the usage and the model used.
    """
    if type(usage) == GenerateContentResponseUsageMetadata:
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count
    elif type(usage) == CompletionUsage:
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
    else:
        raise ValueError("Invalid usage type")

    cost = (llm_costs[model]["input"] / 1000) * input_tokens
    cost += (llm_costs[model]["output"] / 1000) * output_tokens
    return cost


def increase_costs_for_episode_from_usage(episode: 'Episode', usage: CompletionUsage | GenerateContentResponseUsageMetadata, model="gpt-4o-mini-2024-07-18"):
    """
    Increase the cost of an episode by the cost of the given usage.
    """
    increase_costs_for_episode(episode, calculate_llm_costs(usage, model))


def increase_costs_for_episode(episode: 'Episode', cost: float):
    """
    Increase the cost of an episode by the given amount.
    """
    episode.cost = (episode.cost or 0) + cost
    print("Cost:", "$", cost, " Total:", "$", episode.cost)
    episode.save()