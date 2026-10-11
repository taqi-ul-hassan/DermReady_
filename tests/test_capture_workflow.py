from PIL import Image
from src.capture_review import CAPTURE_CHECKLIST, checklist_progress, compare_captures, indicator_rows
from src.inference import Predictor


def test_duplicate_upload_and_dimension_changes_are_explained():
    image=Image.new('RGB',(300,300),'gray')
    assert 'identical decoded pixels' in compare_captures(image,image)[3]
    note=compare_captures(image,Image.new('RGB',(800,300),'gray'))[3]
    assert 'Aspect ratio' in note and 'twofold' in note


def test_checklist_is_self_reported_without_quality_score():
    assert '0 of 4' in checklist_progress([])
    assert '4 of 4' in checklist_progress(CAPTURE_CHECKLIST)
    assert 'do not change' in checklist_progress(CAPTURE_CHECKLIST)
    assert '1 of 4' in checklist_progress([CAPTURE_CHECKLIST[0]]*2+['unknown'])


def test_indicator_references_absent_in_fallback_are_explicit(tmp_path):
    result=Predictor(tmp_path,tmp_path).predict(Image.new('RGB',(300,300),'gray'))
    rows=indicator_rows(result,None)
    assert len(rows)==6 and all(len(row)==3 for row in rows)
    assert rows[0][2]=='No reference available'
