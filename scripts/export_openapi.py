"""Generate OpenAPI including shared contracts consumed by later routes."""
import json
from pathlib import Path
from pydantic.json_schema import models_json_schema
from nextstep.app import app
from nextstep import models
contracts = [getattr(models, name) for name in ('StudentProfile','Scenario','EvidenceRef','Condition','ConditionResult','Scholarship','NormalizedDocument','Chunk','MatchResult','RetrievalRequest','RetrievedEvidence','AnswerResult','ChatTurn','EvalCase','EvalResult')]
_, schema = models_json_schema([(model, 'validation') for model in contracts], ref_template='#/components/schemas/{model}')
api = app.openapi()
api.setdefault('components', {}).setdefault('schemas', {}).update(schema['$defs'])
Path('frontend/openapi.json').write_text(json.dumps(api, indent=2) + '\n')
