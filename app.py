"""Local-first Gradio research demo; no disease diagnosis or upload persistence by app."""
import argparse
import os
from pathlib import Path
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED','False')
os.environ.setdefault('GRADIO_TEMP_DIR',str(Path('.cache/gradio').resolve()))
import gradio as gr
from PIL import ImageOps,Image
from src.inference import Predictor
from src.feedback import NOTICE


def build_app(predictor=None):
    predictor=predictor or Predictor(os.environ.get('DERMREADY_CHECKPOINT_DIR','checkpoints'))
    def analyze(filepath):
        if not filepath:return None,'Choose a photograph',[], 'Upload one PNG, JPEG, or still WebP image.', ''
        try:
            result=predictor.predict(filepath)
        except ValueError as exc:
            return None,'Unable to assess',[],str(exc),''
        except Exception:
            return None,'Unable to assess',[],'The image could not be processed. Try another image or restart the local app.',''
        f=result['features'];m=result['metadata']
        indicators=[['Focus proxy',f"{f['blur_log_laplacian']:.2f}"],
                    ['Mean brightness',f"{100*f['brightness_mean']:.1f}%"],
                    ['Dark pixels',f"{100*f['dark_fraction']:.1f}%"],
                    ['Bright pixels',f"{100*f['bright_fraction']:.1f}%"],
                    ['Contrast proxy',f"{f['contrast_std']:.3f}"],
                    ['Resolution',f"{m['width']} × {m['height']} pixels"]]
        detail=f"Active system: {result['model']}. "
        if result['score'] is not None:detail+=f"Uncalibrated research score: {result['score']:.3f}. "
        detail+='Single-image estimate uses weak case-label validation. The score is not a probability of clinical adequacy.'
        preview=ImageOps.contain(result['preview'],(720,720),Image.Resampling.LANCZOS)
        return preview,result['state'].capitalize(),indicators,result['feedback'],detail
    with gr.Blocks(title='DermReady',analytics_enabled=False,delete_cache=(30,60)) as demo:
        gr.Markdown('# DermReady\n### Prepare a clearer photograph for dermatology review')
        gr.Markdown(NOTICE)
        with gr.Row():
            with gr.Column(scale=1):
                upload=gr.File(label='Upload one photograph',file_count='single',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath')
                gr.Markdown('Up to 20 MB and 24 megapixels. Use the original photograph and your clinician’s requested views.')
                button=gr.Button('Check photograph',variant='primary')
                clear=gr.Button('Clear photograph')
            with gr.Column(scale=1):
                preview=gr.Image(label='Your photograph',interactive=False)
                state=gr.Textbox(label='Research assessment',interactive=False)
        with gr.Row():
            indicators=gr.Dataframe(headers=['Capture indicator','Value'],datatype=['str','str'],interactive=False,label='Image indicators')
            feedback=gr.Textbox(label='Suggested next action',lines=8,interactive=False)
        with gr.Accordion('How to interpret this result',open=False):
            detail=gr.Textbox(label='Research estimate',interactive=False)
            gr.Markdown('Focus and exposure values are imperfect proxies. Framing and unrelated-image detection are not validated. A retake may not fix insufficient clinical information. Held-out results are limited and use case labels as a single-image proxy; clinical adequacy is not established.')
        gr.Markdown('**Upload handling:** the application does not save uploads in its dataset or logs. Gradio uses temporary upload/preview files, with cleanup configured for files older than 60 seconds, checked every 30 seconds. Clearing resets the view; browser and hosting caches may persist. This demo binds to localhost by default.')
        button.click(analyze,inputs=upload,outputs=[preview,state,indicators,feedback,detail],api_name='assess',concurrency_limit=1)
        clear.click(lambda:(None,None,'',[],'',''),outputs=[upload,preview,state,indicators,feedback,detail],api_name=False)
    return demo


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint-dir',default=os.environ.get('DERMREADY_CHECKPOINT_DIR','checkpoints'))
    p.add_argument('--model',choices=['cnn','quality_baseline']);p.add_argument('--port',type=int,default=7860)
    args=p.parse_args();predictor=Predictor(args.checkpoint_dir,model_name=args.model)
    demo=build_app(predictor)
    demo.launch(server_name='127.0.0.1',server_port=args.port,share=False,show_error=False,
                blocked_paths=[str(Path(p).resolve()) for p in ['data',args.checkpoint_dir,'.env']],
                max_file_size='20mb',run_history=False,enable_monitoring=False,mcp_server=False)

if __name__=='__main__':main()
