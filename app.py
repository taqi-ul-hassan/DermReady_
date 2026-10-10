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
from src.capture_review import compare_captures, evidence_summary, primary_action

ROOT = Path(__file__).resolve().parent


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
        guidance = 'Next action: ' + primary_action(result) + '\n\n' + result['feedback']
        return preview,result['state'].capitalize(),indicators,guidance,detail
    def compare(original, retake):
        try:
            first, second, rows, notes = compare_captures(original, retake)
            return (ImageOps.contain(first,(720,720)), ImageOps.contain(second,(720,720)), rows, notes)
        except ValueError as exc:
            return None,None,[],str(exc)
        except Exception:
            return None,None,[],'Comparison could not be completed. Try two valid still photographs.'
    with gr.Blocks(title='DermReady',analytics_enabled=False,delete_cache=(30,60)) as demo:
        gr.Markdown('# DermReady\n### Check your capture. Improve it. Compare again.')
        gr.Markdown(NOTICE)
        mode_label = 'Capture indicators only — fitted artifacts are unavailable' if predictor.mode == 'features_only' else 'Fitted research system: ' + predictor.mode
        gr.Markdown('**Current mode:** ' + mode_label)
        gr.Markdown('**1. Check** an original photograph below. **2. Capture again** using supported guidance. **3. Compare** both photographs before deciding what to send to your clinician.')
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
        with gr.Accordion('Try a permitted example',open=False):
            gr.Markdown('These artificial capture targets contain no patients or skin photographs. They demonstrate indicator behavior, not clinical accuracy. Missing artifacts keep every suitability result uncertain.')
            gr.Examples(examples=[[str(ROOT/'assets/demo'/name)] for name in ['synthetic_original.png','synthetic_blur.png','synthetic_dark.png','synthetic_noise.png']],inputs=upload)
        with gr.Accordion('Compare an original and a new capture',open=False):
            gr.Markdown('Upload two independently captured photographs with similar framing. This compares measurable signals; it does not judge which photograph is clinically adequate or modify either image.')
            with gr.Row():
                original=gr.File(label='Original photograph',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath')
                retake=gr.File(label='New capture',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath')
            compare_button=gr.Button('Compare capture indicators',variant='primary')
            with gr.Row():
                original_preview=gr.Image(label='Original',interactive=False)
                retake_preview=gr.Image(label='New capture',interactive=False)
            differences=gr.Dataframe(headers=['Indicator','Original','New capture','Change'],datatype=['str','number','number','number'],interactive=False)
            comparison_notes=gr.Textbox(label='What changed — and what it means',lines=6,interactive=False)
            compare_clear=gr.Button('Clear comparison')
            compare_button.click(compare,inputs=[original,retake],outputs=[original_preview,retake_preview,differences,comparison_notes],api_name='compare_captures',concurrency_limit=1)
            compare_clear.click(lambda:(None,None,None,None,[],''),outputs=[original,retake,original_preview,retake_preview,differences,comparison_notes],api_name=False)
        with gr.Accordion('Evidence and limitations',open=False):
            gr.Markdown('### Frozen evaluation, separate from your upload\n107 held-out cases: 23 ungradable and 84 gradable. Each contributes one first-listed image with a **weak case-label proxy**, not a clinical image-level label. The default baseline returned 12 suitable, 34 retake, and 61 uncertain outputs.')
            evidence=evidence_summary(ROOT/'reports/heldout_test.json')
            gr.Dataframe(value=evidence,headers=['System','False acceptance','False rejection','Decision coverage','Uncertain'],datatype=['str']*5,interactive=False)
            gr.Markdown('Error denominators include all cases of the corresponding class, including uncertain outputs. Coverage means a suitable or retake output. Baseline false acceptance: **1/23**, 95% interval **0.8–21.0%**; false rejection: **25/84**. These small-sample results do not establish clinical safety. The baseline was selected on validation; no model or threshold was changed after the test. No skin detector, framing assessment, or subgroup assurance is established.')
            gr.Image(value=str(ROOT/'reports/robustness_states.png'),label='Frozen blur and lighting sensitivity experiments',interactive=False)
            gr.Markdown('Edited images have no new clinical labels. These experiments demonstrate sensitivity to synthetic changes, not clinical accuracy. See reports/heldout_test.md, reports/robustness.md and docs/MODEL_CARD.md in the repository for full evidence.')
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
                max_file_size='20mb',run_history=False,enable_monitoring=False,mcp_server=False,
                theme=gr.themes.Soft(primary_hue='teal',neutral_hue='slate'))

if __name__=='__main__':main()
