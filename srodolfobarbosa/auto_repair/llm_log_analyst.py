"""LLM Log Analyst

Provides an adapter to analyze CI logs with a pluggable LLM provider.

Usage:
  from srodolfobarbosa.auto_repair.llm_log_analyst import LLMLogAnalyst
  analyst = LLMLogAnalyst()
  result = analyst.analyze(log_text, metadata={})

The implementation includes a simple file cache and a 'mock' provider for local testing.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

CACHE_DIR = Path(".cache/llm_log_analyst")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class LLMLogResult:
    causa_raiz: str
    sugestao_patch: Optional[str]
    comandos_de_teste: Optional[str]
    confianca: float
    explicacao: str


class LLMLogAnalyst:
    def __init__(self, provider: Optional[str] = None, timeout: int = 30):
        self.provider = provider or os.environ.get("LLM_PROVIDER", "mock")
        self.timeout = timeout

    def _cache_path(self, text: str) -> Path:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return CACHE_DIR / f"{h}.json"

    def _load_cache(self, text: str) -> Optional[LLMLogResult]:
        p = self._cache_path(text)
        if p.exists():
            obj = json.loads(p.read_text(encoding="utf-8"))
            return LLMLogResult(**obj)
        return None

    def _write_cache(self, text: str, result: LLMLogResult):
        p = self._cache_path(text)
        p.write_text(json.dumps(result.__dict__), encoding="utf-8")

    def _call_provider(self, text: str, metadata: Dict) -> Dict:
        """Pluggable providers. Currently supports 'mock' and 'openai' (if available).
        The method returns a dict with keys matching LLMLogResult fields."""
        if self.provider == "mock":
            # Very simple heuristic for mocks: look for keywords
            if "ImportError" in text or "No module named" in text:
                return {
                    "causa_raiz": "ImportError / dependencia faltando",
                    "sugestao_patch": None,
                    "comandos_de_teste": "pip install -r requirements.txt && pytest -q",
                    "confianca": 0.7,
                    "explicacao": "Detectado ImportError. Sugestão: instalar dependências faltantes e reexecutar testes.",
                }
            if "flake8" in text or "E402" in text:
                return {
                    "causa_raiz": "Problemas de estilo (imports fora do topo ou format)",
                    "sugestao_patch": None,
                    "comandos_de_teste": "ruff check --fix . || true",
                    "confianca": 0.6,
                    "explicacao": "Erros de lint detectados; aplicar ruff --fix e re-testar.",
                }
            # fallback generic
            return {
                "causa_raiz": "Erro desconhecido (resumo heurístico)",
                "sugestao_patch": None,
                "comandos_de_teste": "pytest -q",
                "confianca": 0.4,
                "explicacao": "Sugestão genérica: rodar testes e aplicar fixes de estilo.",
            }
        elif self.provider == "openai":
            try:
                import openai

                openai.api_key = os.environ.get("OPENAI_API_KEY")
                prompt = (
                    "You are a helpful devops assistant. Given the following CI log, "
                    "extract the root cause, suggest a minimal patch (unified diff) if possible, "
                    "provide the test commands to validate the fix, and give a confidence score (0-1).\n\n"
                    f"LOG:\n{text[:4000]}"
                )
                resp = openai.ChatCompletion.create(model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), messages=[{"role":"user","content":prompt}], timeout=self.timeout)
                content = resp.choices[0].message.content
                # Expect the model to return a JSON — attempt to parse
                try:
                    obj = json.loads(content)
                except Exception:
                    # fallback: wrap model text
                    obj = {"causa_raiz": content, "sugestao_patch": None, "comandos_de_teste": None, "confianca": 0.5, "explicacao": content}
                return obj
            except Exception as e:
                return {"causa_raiz": f"LLM error: {e}", "sugestao_patch": None, "comandos_de_teste": None, "confianca": 0.0, "explicacao": str(e)}
        else:
            raise ValueError(f"Provider {self.provider} not supported")

    def analyze(self, log_text: str, metadata: Optional[Dict] = None, use_cache: bool = True) -> LLMLogResult:
        if metadata is None:
            metadata = {}
        if use_cache:
            cached = self._load_cache(log_text)
            if cached:
                return cached
        obj = self._call_provider(log_text, metadata)
        res = LLMLogResult(
            causa_raiz=obj.get("causa_raiz", ""),
            sugestao_patch=obj.get("sugestao_patch"),
            comandos_de_teste=obj.get("comandos_de_teste"),
            confianca=float(obj.get("confianca", 0.0)),
            explicacao=obj.get("explicacao", ""),
        )
        if use_cache:
            try:
                self._write_cache(log_text, res)
            except Exception:
                pass
        return res
