from __future__ import annotations

import json
import re

from google import genai
from google.genai import types

from nsjudge.config import Settings
from nsjudge.prompts import (
    CONTRACT_GENERATION_PROMPT,
    DEPENDENCY_CONTEXT_TEMPLATE,
    REFINEMENT_PROMPT,
    SINGLE_DEPENDENCY_TEMPLATE,
    SYSTEM_PROMPT,
)
from nsjudge.schemas import (
    FunctionContract,
    FunctionInfo,
    RefinementRequest,
    TokenUsage,
    VerifiedContract,
)


class SemanticTranslator:
    """Bridges source code and Z3 constraints via Gemini LLM."""

    def __init__(self, settings: Settings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=FunctionContract,
            temperature=0.2,
        )

    def generate_contract(
        self,
        func_info: FunctionInfo,
        verified_deps: dict[str, VerifiedContract] | None = None,
    ) -> tuple[FunctionContract, TokenUsage]:
        """Generate a formal contract and Z3 script for a function."""
        dependency_context = self._build_dependency_context(verified_deps or {})

        prompt = CONTRACT_GENERATION_PROMPT.format(
            function_source=func_info.source,
            function_name=func_info.name,
            parameters=", ".join(func_info.args) if func_info.args else "(none)",
            dependency_context=dependency_context,
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=self._config,
        )
        u = response.usage_metadata
        usage = TokenUsage(
            prompt_tokens=u.prompt_token_count or 0,
            completion_tokens=u.candidates_token_count or 0,
            total_tokens=u.total_token_count or 0,
        )
        return self._parse_response(response.text), usage

    def refine_contract(self, request: RefinementRequest) -> tuple[FunctionContract, TokenUsage]:
        """Ask the LLM to fix a broken Z3 script."""
        prompt = REFINEMENT_PROMPT.format(
            function_name=request.original_contract.function_name,
            error_traceback=request.error_traceback,
            original_z3_script=request.original_contract.z3_script,
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=self._config,
        )
        u = response.usage_metadata
        usage = TokenUsage(
            prompt_tokens=u.prompt_token_count or 0,
            completion_tokens=u.candidates_token_count or 0,
            total_tokens=u.total_token_count or 0,
        )
        return self._parse_response(response.text), usage

    def _build_dependency_context(
        self, verified_deps: dict[str, VerifiedContract]
    ) -> str:
        """Build the prompt section describing already-verified dependencies."""
        if not verified_deps:
            return ""

        contracts_text = []
        for dep in verified_deps.values():
            contracts_text.append(
                SINGLE_DEPENDENCY_TEMPLATE.format(
                    function_name=dep.function_name,
                    parameters=", ".join(
                        dep.contract.preconditions[:1]
                    ),  # Brief summary
                    preconditions="; ".join(dep.contract.preconditions),
                    postconditions="; ".join(dep.contract.postconditions),
                )
            )

        return DEPENDENCY_CONTEXT_TEMPLATE.format(
            contracts="\n".join(contracts_text)
        )

    @staticmethod
    def _sanitize_json(text: str) -> str:
        """Fix common LLM JSON issues: unescaped control chars in strings."""
        # Replace literal newlines/tabs inside JSON string values with escaped versions
        # Process character by character, tracking whether we're inside a JSON string
        result = []
        in_string = False
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '"' and (i == 0 or text[i - 1] != "\\"):
                in_string = not in_string
                result.append(ch)
            elif in_string and ch == "\n":
                result.append("\\n")
            elif in_string and ch == "\t":
                result.append("\\t")
            elif in_string and ch == "\r":
                result.append("\\r")
            else:
                result.append(ch)
            i += 1
        return "".join(result)

    @staticmethod
    def _parse_response(response_text: str) -> FunctionContract:
        """Parse LLM JSON response into a FunctionContract."""
        # Try direct parse first
        try:
            data = json.loads(response_text)
            return FunctionContract(**data)
        except json.JSONDecodeError:
            pass

        # Try with sanitized control characters
        try:
            sanitized = SemanticTranslator._sanitize_json(response_text)
            data = json.loads(sanitized)
            return FunctionContract(**data)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            sanitized = SemanticTranslator._sanitize_json(match.group(1))
            data = json.loads(sanitized)
            return FunctionContract(**data)

        # Try finding the first { ... } block
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            sanitized = SemanticTranslator._sanitize_json(match.group(0))
            data = json.loads(sanitized)
            return FunctionContract(**data)

        raise ValueError(f"Could not parse LLM response as JSON: {response_text[:200]}")
