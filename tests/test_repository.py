import pytest
from sqlalchemy import create_engine
from nextstep.db import metadata
from nextstep.repository import Repository
from nextstep.models import Scholarship

def test_staging_activation_and_compare_swap():
    engine = create_engine('sqlite://')
    metadata.create_all(engine)
    repo = Repository(engine)
    repo.stage_catalog('v1', [Scholarship(id='one', corpus_version='v1', name='One')])
    assert repo.active_version() is None
    repo.activate_version(None, 'v1')
    assert repo.list_scholarships(repo.active_version())[0].id == 'one'
    repo.stage_catalog('v2', [])
    with pytest.raises(ValueError):
        repo.activate_version(None, 'v2')
    assert repo.active_version() == 'v1'

def test_duplicate_ids_rejected():
    engine = create_engine('sqlite://')
    metadata.create_all(engine)
    row = Scholarship(id='one', corpus_version='v1', name='One')
    with pytest.raises(ValueError):
        Repository(engine).stage_catalog('v1', [row, row])
