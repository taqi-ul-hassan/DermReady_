from pathlib import Path
from app import build_app
from src.inference import Predictor
from src.session_review import ReviewSession


def functions(app):
    return {fn.fn.__name__:fn.fn for fn in app.fns.values() if fn.fn is not None}


def test_changed_upload_and_clear_remove_every_old_result(tmp_path):
    app=build_app(Predictor(tmp_path,report_dir=tmp_path));f=functions(app);session=ReviewSession()
    result=f['reset_review']('current.png',session)
    assert result[0] is None and result[2]==[] and result[4]==''
    assert result[1]=='Awaiting assessment' and 'changed' in result[3]
    assert f['reset_review'](None,session)[1]=='Choose a photograph'
    assert f['clear_review'](session)==(None,None,'',[],'','')
    reset_ids={key for key,fn in app.fns.items() if fn.fn is not None and fn.fn.__name__=='reset_review'}
    assert any(dep['id'] in reset_ids and any(target[1]=='change' for target in dep['targets']) for dep in app.config['dependencies'])


def test_either_comparison_upload_invalidates_old_pair(tmp_path):
    app=build_app(Predictor(tmp_path,report_dir=tmp_path));f=functions(app);session=ReviewSession()
    result=f['reset_comparison']('original.png','new.png',session)
    assert result[:3]==(None,None,[]) and 'changed' in result[3]
    assert 'Choose both' in f['reset_comparison'](None,'new.png',session)[3]
    reset_ids={key for key,fn in app.fns.items() if fn.fn is not None and fn.fn.__name__=='reset_comparison'}
    assert sum(dep['id'] in reset_ids for dep in app.config['dependencies'])==2
    assert not any(c['props'].get('elem_id')=='research-notice' for c in app.config['components'])
    assert any('Research prototype only' in c['props'].get('value','') for c in app.config['components'] if isinstance(c['props'].get('value'),str))
