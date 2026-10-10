"""Download/decode train+validation images only; test images untouched by default."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import quote
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
import pandas as pd
from src.preprocessing import load_image


def cache(processed_dir, raw_dir, report_dir, splits=('train','validation')):
    processed_dir, raw_dir, report_dir = map(Path,(processed_dir,raw_dir,report_dir))
    table=pd.read_csv(processed_dir/'images.csv',dtype={'case_id':str},keep_default_na=False)
    rows=table[table.split.isin(splits)].drop_duplicates('image_path').to_dict('records')
    target=raw_dir/'images';target.mkdir(parents=True,exist_ok=True)
    with httpx.Client(timeout=60,follow_redirects=True) as client:
        def process(row):
            path=row['image_path']
            record={'image_path':path,'split':row['split']}
            try:
                if not path.startswith('dataset/images/') or '..' in path.split('/'):
                    raise ValueError('Unexpected SCIN object path')
                local=target/Path(path).name
                expected=row['content_md5']
                valid_cache=local.exists() and (not expected or base64.b64encode(hashlib.md5(local.read_bytes()).digest()).decode()==expected)
                if not valid_cache:
                    for attempt in range(3):
                        try:
                            response=client.get('https://storage.googleapis.com/dx-scin-public-data/'+quote(path,safe='/'))
                            response.raise_for_status();blob=response.content
                            if expected and base64.b64encode(hashlib.md5(blob).digest()).decode()!=expected:
                                raise ValueError('Object MD5 does not match saved inventory')
                            temp=local.with_suffix(local.suffix+'.part');temp.write_bytes(blob);temp.replace(local)
                            break
                        except Exception:
                            if attempt==2: raise
                _, metadata=load_image(local)
                record.update(readable=True,**metadata)
            except Exception as exc:
                record.update(readable=False,error=str(exc))
            return record
        with ThreadPoolExecutor(max_workers=8) as pool:
            checks=list(pool.map(process,rows))
    (raw_dir/'decode_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    failures=[r for r in checks if not r['readable']]
    report={'splits_checked':list(splits),'unique_images_checked':len(checks),
            'readable_images':len(checks)-len(failures),'failed_images':len(failures),
            'test_images_decoded':'test' in splits,'limits':{'max_file_mb':20,'max_pixels':24000000},
            'transform':'EXIF transpose, RGB conversion, entire-image letterbox to 224, ImageNet normalization; train-only horizontal flip',
            'status':'passed' if not failures else 'blocked: inspect private decode_checks.json before training'}
    report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/'preprocessing_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--processed-dir',default='data/processed');p.add_argument('--raw-dir',default='data/raw');p.add_argument('--report-dir',default='reports')
    args=p.parse_args();report=cache(args.processed_dir,args.raw_dir,args.report_dir);print(json.dumps(report,indent=2))
    if report['failed_images']:raise SystemExit(1)
