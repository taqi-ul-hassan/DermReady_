import sys
import app


def test_cloud_startup_uses_provider_port_and_blocks_secret_mirrors(monkeypatch,tmp_path):
    captured={}
    class Demo:
        def launch(self,**kwargs):captured.update(kwargs)
    def build(predictor,public_demo=False):
        captured['public_demo']=public_demo
        return Demo()
    monkeypatch.setattr(app,'build_app',build)
    monkeypatch.setenv('PORT','10000')
    monkeypatch.setattr(sys,'argv',['app.py','--host','0.0.0.0','--checkpoint-dir',str(tmp_path)])
    app.main()
    assert captured['server_name']=='0.0.0.0' and captured['server_port']==10000
    assert captured['public_demo'] and captured['share'] is False
    assert str(app.ROOT/'quality_baseline.json') in captured['blocked_paths']
    assert str(app.ROOT/'decision_policy.json') in captured['blocked_paths']
    assert str(tmp_path.resolve()) in captured['blocked_paths']


def test_local_startup_remains_private_by_default(monkeypatch,tmp_path):
    captured={}
    class Demo:
        def launch(self,**kwargs):captured.update(kwargs)
    monkeypatch.setattr(app,'build_app',lambda predictor,public_demo=False:Demo())
    monkeypatch.delenv('PORT',raising=False)
    monkeypatch.setattr(sys,'argv',['app.py','--checkpoint-dir',str(tmp_path)])
    app.main()
    assert captured['server_name']=='127.0.0.1' and captured['server_port']==7860
    assert captured['share'] is False
