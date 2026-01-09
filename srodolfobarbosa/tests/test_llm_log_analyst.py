import sys
import os

# ensure repo root is on sys.path for imports when running tests in CI
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# Now the project root is on sys.path; importing top-level modules like `deus` will work for tests that expect that layout.
from srodolfobarbosa.auto_repair.llm_log_analyst import LLMLogAnalyst


def test_mock_importerror():
    analyst = LLMLogAnalyst(provider="mock")
    log = "Traceback (most recent call last):\n  File \"/app/foo.py\", line 1, in <module>\nImportError: No module named 'pinecone'\n"
    res = analyst.analyze(log)
    assert "ImportError" in res.causa_raiz or "dependencia" in res.causa_raiz
    assert res.comandos_de_teste is not None


def test_cache_behavior(tmp_path):
    analyst = LLMLogAnalyst(provider="mock")
    log = "Test message: E402 Module level import not at top of file"
    # clear cache if exists
    import hashlib

    h = hashlib.sha256(log.encode("utf-8")).hexdigest()
    p = tmp_path / f"{h}.json"
    # use local cache dir by monkeypatching

    orig = analyst._cache_path

    def tmp_cache_path(text):
        return p

    analyst._cache_path = tmp_cache_path

    # first call writes cache
    res1 = analyst.analyze(log, use_cache=True)
    assert p.exists()

    # modify cache contents to fake different result
    p.write_text(
        '{"causa_raiz": "X", "sugestao_patch": null, "comandos_de_teste": "ruff", "confianca": 0.9, "explicacao": "cached"}'
    )

    res2 = analyst.analyze(log, use_cache=True)
    assert res2.causa_raiz == "X"
