"""Exercise local Gradio upload API with synthetic data and private-path blocking."""
import json
import argparse
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['NO_PROXY']=','.join(filter(None,[os.environ.get('NO_PROXY',''),'127.0.0.1','localhost']))
import httpx
import numpy as np
from PIL import Image
from gradio_client import Client,handle_file
from app import build_app
from src.inference import Predictor


def main(output='.cache/app_smoke_test.json'):
    path=Path('.cache/smoke_test.png');path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.random.default_rng(42).integers(20,230,(400,400,3),dtype=np.uint8)).save(path)
    demo=build_app(Predictor())
    try:
        _,url,_=demo.launch(server_name='127.0.0.1',server_port=7862,share=False,prevent_thread_lock=True,quiet=True,
            blocked_paths=[str(Path(p).resolve()) for p in ['data','checkpoints','.env']],max_file_size='20mb',
            run_history=False,enable_monitoring=False,mcp_server=False)
        client=Client(url,verbose=False)
        result=client.predict(handle_file(str(path.resolve())),api_name='/assess')
        assert result[1]=='Uncertain', 'Synthetic noise must be outside the texture reference range'
        assert result[2] and result[3]
        assert 'Next action:' in result[3]
        comparison=client.predict(handle_file(str(Path('assets/demo/synthetic_blur.png').resolve())),
            handle_file(str(Path('assets/demo/synthetic_original.png').resolve())),api_name='/compare_captures')
        assert comparison[0] and comparison[1]
        assert comparison[2]['data'][0][3]>0
        assert 'No clinical improvement or suitability is established' in comparison[3]
        response=httpx.get(url+'gradio_api/file='+str(Path('data/raw/scin_cases.csv').resolve()),trust_env=False)
        assert response.status_code in (400,403)
        report={'local_server_started':True,'upload_api_success':True,'result_state':result[1],
                'private_dataset_http_status':response.status_code,'private_dataset_serving_blocked':True,
                'public_share_enabled':False,'test_images_used':False,'synthetic_upload_only':True,
                'retake_comparison_api_success':True,
                'temporary_file_cleanup_config_seconds':[30,60]}
        destination=Path(output);destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
    finally:demo.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='.cache/app_smoke_test.json')
    main(parser.parse_args().output)
