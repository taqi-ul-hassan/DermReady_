"""Verify reference UI construction and live assessment/retake APIs with synthetic inputs."""
import os
os.environ['NO_PROXY']=','.join(filter(None,[os.environ.get('NO_PROXY',''),'127.0.0.1','localhost']))
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import httpx
from gradio_client import Client,handle_file
from app import build_app
from src.inference import Predictor
from src.ui_style import CSS,app_theme

root=Path(__file__).resolve().parents[1]
predictor=Predictor(root/'checkpoints',root/'reports')
app=build_app(predictor)
try:
    _,url,_=app.launch(server_name='127.0.0.1',server_port=7863,share=False,prevent_thread_lock=True,quiet=True,
        theme=app_theme(),css=CSS,footer_links=[],blocked_paths=[str(root/'checkpoints'),str(root/'data')],
        max_file_size='20mb',run_history=False,enable_monitoring=False,mcp_server=False)
    client=Client(url,verbose=False)
    result=client.predict(handle_file(str(root/'assets/demo/synthetic_noise.png')),api_name='/assess')
    assert result[1]=='Uncertain' and result[2] and result[3]
    compared=client.predict(handle_file(str(root/'assets/demo/synthetic_blur.png')),
        handle_file(str(root/'assets/demo/synthetic_original.png')),api_name='/compare_captures')
    assert compared[0] and compared[1] and compared[2] and 'clinical' in compared[3]
    response=httpx.get(url+'config',trust_env=False);response.raise_for_status();config=response.json()
    tabs=[c['props']['label'] for c in config['components'] if c['type']=='tabitem']
    assert tabs==['Check a photograph','Compare a retake','Evidence & limits']
    assert 'derm-hero' in config['components'][0]['props'].get('value','') or any('derm-hero' in c['props'].get('value','') for c in config['components'] if isinstance(c['props'].get('value'),str))
    assert '#00b9ab' in config['css']
    report={'assessment_api':'passed','retake_comparison_api':'passed','tabs':tabs,'reference_css_loaded':True,
        'mode':predictor.mode,'model_changes':False,'browser_visual_comparison':'not performed in this workspace'}
    (root/'reports/frontend_update_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
finally:
    app.close()
