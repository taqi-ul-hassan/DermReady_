from copy import deepcopy
from threading import Event,Thread
from src.session_review import ReviewSession


def test_changing_upload_discards_inflight_result():
    session=ReviewSession();started=Event();finish=Event();output=[]
    def operation():
        started.set();assert finish.wait(2);return 'old image assessment'
    thread=Thread(target=lambda:output.append(session.run(operation)));thread.start()
    assert started.wait(2);session.invalidate();finish.set();thread.join(2)
    assert output==[None]
    assert session.run(lambda:'new image assessment')=='new image assessment'


def test_browser_sessions_are_independent():
    first=ReviewSession();second=deepcopy(first)
    second.invalidate()
    assert first.run(lambda:42)==42
    assert second is not first
