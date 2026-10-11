import json
from src.artifact_identity import artifact_identity, evidence_identity_message, sha256
from scripts.check_installation import check_installation


def test_identity_tracks_active_model_and_changed_policy(tmp_path):
    names=['best.pt','quality_baseline.json','decision_policy.json']
    for name in names:(tmp_path/name).write_text(name)
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'artifact_sha256':{n:sha256(tmp_path/n) for n in names}}))
    identity=artifact_identity(tmp_path,manifest,'quality_baseline')
    assert identity['active_model_matches']
    (tmp_path/'best.pt').unlink()
    assert artifact_identity(tmp_path,manifest,'quality_baseline')['active_model_matches']
    assert not artifact_identity(tmp_path,manifest,'cnn')['active_model_matches']
    (tmp_path/'decision_policy.json').write_text('different')
    identity=artifact_identity(tmp_path,manifest,'quality_baseline')
    assert not identity['active_model_matches']
    assert 'must not be attributed' in evidence_identity_message(identity,'quality_baseline')


def test_missing_manifest_and_indicator_mode_do_not_claim_evaluation_match(tmp_path):
    identity=artifact_identity(tmp_path,tmp_path/'missing.json')
    assert identity['status']=='unavailable' and not identity['active_model_matches']
    assert 'indicators only' in evidence_identity_message(identity,'features_only')


def test_installation_checker_explains_nested_artifacts(tmp_path):
    nested=tmp_path/'extracted';nested.mkdir()
    (nested/'decision_policy.json').write_text('{}')
    report=check_installation(tmp_path)
    assert report['active_model']=='features_only' and not report['trained_ready']
    assert any('nested' in s for s in report['messages'])
