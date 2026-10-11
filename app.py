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
from src.capture_review import indicator_rows, CAPTURE_CHECKLIST, checklist_progress
from src.artifact_identity import artifact_identity, evidence_identity_message
from src.ui_style import HERO, CSS, app_theme
from src.session_review import ReviewSession

ROOT = Path(__file__).resolve().parent


def build_app(predictor=None,public_demo=False):
    predictor=predictor or Predictor(os.environ.get('DERMREADY_CHECKPOINT_DIR',str(ROOT/'checkpoints')),ROOT/'reports')
    def analyze_raw(filepath):
        if not filepath:return None,'Choose a photograph',[], 'Upload one PNG, JPEG, or still WebP image.', ''
        try:
            result=predictor.predict(filepath)
        except ValueError as exc:
            return None,'Unable to assess',[],str(exc),''
        except Exception:
            return None,'Unable to assess',[],'The image could not be processed. Try another image or restart the local app.',''
        indicators=indicator_rows(result,predictor.quality_thresholds)
        detail=f"Active system: {result['model']}. "
        if result['score'] is not None:detail+=f"Uncalibrated research score: {result['score']:.3f}. "
        detail+='Single-image estimate uses weak case-label validation. The score is not a probability of clinical adequacy.'
        preview=ImageOps.contain(result['preview'],(720,720),Image.Resampling.LANCZOS)
        guidance = 'Why this result: ' + result['decision_reason'] + '\n\nNext action: ' + primary_action(result) + '\n\n' + result['feedback']
        return preview,result['state'].capitalize(),indicators,guidance,detail
    def compare_raw(original, retake):
        try:
            first, second, rows, notes = compare_captures(original, retake)
            return (ImageOps.contain(first,(720,720)), ImageOps.contain(second,(720,720)), rows, notes)
        except ValueError as exc:
            return None,None,[],str(exc)
        except Exception:
            return None,None,[],'Comparison could not be completed. Try two valid still photographs.'
    def analyze(filepath,session):
        result=session.run(lambda:analyze_raw(filepath))
        return result if result is not None else tuple(gr.skip() for _ in range(5))
    def compare(original,retake,session):
        result=session.run(lambda:compare_raw(original,retake))
        return result if result is not None else tuple(gr.skip() for _ in range(4))
    def reset_review(filepath,session):
        session.invalidate()
        if not filepath:return None,'Choose a photograph',[],'Upload one PNG, JPEG, or still WebP image.',''
        return None,'Awaiting assessment',[],'Photograph changed. Click Check photograph to assess the current upload.',''
    def reset_comparison(original,retake,session):
        session.invalidate()
        note='Photographs changed. Compare the current captures again.' if original and retake else 'Choose both the original photograph and a new capture.'
        return None,None,[],note
    def clear_review(session):
        session.invalidate()
        return None,None,'',[],'',''
    def clear_comparison(session):
        session.invalidate()
        return None,None,None,None,[],''
    with gr.Blocks(title='DermReady',analytics_enabled=False,delete_cache=(30,60)) as demo:
        gr.HTML(HERO)
        review_session=gr.State(ReviewSession(),time_to_live=3600)
        comparison_session=gr.State(ReviewSession(),time_to_live=3600)
        mode_label = 'Capture indicators only — fitted artifacts are unavailable' if predictor.mode == 'features_only' else 'Fitted research system: ' + predictor.mode
        gr.Markdown('**Current mode:** ' + mode_label,elem_id='mode-banner')
        if public_demo:
            gr.Markdown('**Public hackathon demo:** use the synthetic examples or photographs you have permission to share. Avoid identifiable medical uploads.')
        with gr.Tabs():
            with gr.Tab('Check a photograph'):
                with gr.Row():
                    with gr.Column(scale=1,elem_classes='capture-card'):
                        gr.Markdown('### Start with your original\nUpload a photograph to explore its capture indicators.',elem_classes='section-heading')
                        upload=gr.File(label='Upload one photograph',file_count='single',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath',elem_id='capture-upload')
                        gr.Markdown('Up to 20 MB and 24 megapixels. Use the original photograph and your clinician’s requested views.')
                        button=gr.Button('Check photograph',variant='primary',elem_classes='primary-action')
                        clear=gr.Button('Clear photograph')
                    with gr.Column(scale=1,elem_classes='capture-card'):
                        gr.Markdown('### Your capture review\nYour preview and research assessment appear here.',elem_classes='section-heading')
                        preview=gr.Image(label='Your photograph',interactive=False,elem_id='capture-preview')
                        state=gr.Textbox(label='Research assessment',interactive=False,placeholder='Ready when you are',elem_id='assessment')
                with gr.Row(elem_classes='insights-row'):
                    indicators=gr.Dataframe(headers=['Capture indicator','Value','Interpretation'],datatype=['str']*3,interactive=False,label='Image indicators')
                    feedback=gr.Textbox(label='Suggested next action',lines=8,interactive=False)
                with gr.Accordion('How to interpret this result',open=False):
                    detail=gr.Textbox(label='Research estimate',interactive=False)
                    gr.Markdown('Focus and exposure values are imperfect proxies. Framing and unrelated-image detection are not validated. A retake may not fix insufficient clinical information. Held-out results are limited and use case labels as a single-image proxy; clinical adequacy is not established.')
                    gr.Markdown('**No reference flag** means the distribution-based guard did not trigger. It is not a pass or a guarantee of image quality. **Inspect visually** identifies a signal to check, rather than a confirmed defect.')
                with gr.Accordion('Try a permitted example',open=False):
                    gr.Markdown('These artificial capture targets contain no patients or skin photographs. They demonstrate indicator behavior, not clinical accuracy. Missing artifacts keep every suitability result uncertain.')
                    gr.Examples(examples=[[str(ROOT/'assets/demo'/name)] for name in ['synthetic_original.png','synthetic_blur.png','synthetic_dark.png','synthetic_noise.png']],inputs=upload)
            with gr.Tab('Compare a retake'):
                gr.Markdown('### Small changes, side by side',elem_classes='comparison-heading')
                gr.Markdown('Upload two independently captured photographs with similar framing. This compares measurable signals; it does not judge which photograph is clinically adequate or modify either image.')
                with gr.Accordion('Prepare your next capture',open=False):
                    checklist=gr.CheckboxGroup(choices=CAPTURE_CHECKLIST,value=[],interactive=True,label='Your preparation checklist (optional)',elem_id='capture-checklist')
                    progress=gr.Markdown(checklist_progress([]))
                    checklist.change(checklist_progress,inputs=checklist,outputs=progress,api_name=False,queue=False)
                with gr.Row():
                    original=gr.File(label='Original photograph',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath')
                    retake=gr.File(label='New capture',file_types=['.png','.jpg','.jpeg','.webp'],type='filepath')
                compare_button=gr.Button('Compare capture indicators',variant='primary',elem_classes='primary-action')
                with gr.Row():
                    original_preview=gr.Image(label='Original',interactive=False)
                    retake_preview=gr.Image(label='New capture',interactive=False)
                differences=gr.Dataframe(headers=['Indicator','Original','New capture','Change'],datatype=['str','number','number','number'],interactive=False)
                comparison_notes=gr.Textbox(label='What changed — and what it means',lines=6,interactive=False)
                compare_clear=gr.Button('Clear comparison')
                compare_button.click(compare,inputs=[original,retake,comparison_session],outputs=[original_preview,retake_preview,differences,comparison_notes],api_name='compare_captures',concurrency_limit=1,concurrency_id='capture-processing')
                compare_clear.click(clear_comparison,inputs=comparison_session,outputs=[original,retake,original_preview,retake_preview,differences,comparison_notes],api_name=False,queue=False)
                for capture in (original,retake):
                    capture.change(reset_comparison,inputs=[original,retake,comparison_session],outputs=[original_preview,retake_preview,differences,comparison_notes],api_name=False,queue=False)
            with gr.Tab('Evidence & limits'):
                gr.Markdown(NOTICE)
                identity=artifact_identity(predictor.directory,ROOT/'reports/model_artifacts.json',predictor.mode)
                gr.Markdown('**Evidence provenance:** '+evidence_identity_message(identity,predictor.mode))
                gr.Markdown('### Frozen evaluation, separate from your upload\n107 held-out cases: 23 ungradable and 84 gradable. Each contributes one first-listed image with a **weak case-label proxy**, not a clinical image-level label. The default baseline returned 12 suitable, 34 retake, and 61 uncertain outputs.')
                evidence=evidence_summary(ROOT/'reports/heldout_test.json')
                gr.Dataframe(value=evidence,headers=['System','False acceptance','False rejection','Decision coverage','Uncertain'],datatype=['str']*5,interactive=False)
                gr.Markdown('Error denominators include all cases of the corresponding class, including uncertain outputs. Coverage means a suitable or retake output. Baseline false acceptance: **1/23**, 95% interval **0.8–21.0%**; false rejection: **25/84**. These small-sample results do not establish clinical safety. The baseline was selected on validation; no model or threshold was changed after the test. No skin detector, framing assessment, or subgroup assurance is established.')
                gr.Markdown('**Why uncertain is common:** the default pipeline was uncertain on 61/107 cases. Its wide score band and capture guards reflect limited evidence. Brightness depends on skin tone, background and lighting, and is not a skin-tone measurement. Performance by skin tone, age, condition and device is not established. Dermoscopic, histology, pediatric and outside-source images have no separate validation. See docs/TECHNICAL_BIAS_AUDIT.md for the review.')
                gr.Markdown('#### Frozen blur and lighting sensitivity experiments')
                gr.Image(value=str(ROOT/'reports/robustness_states.png'),show_label=False,interactive=False)
                gr.Markdown('Edited images have no new clinical labels. These experiments demonstrate sensitivity to synthetic changes, not clinical accuracy. See reports/heldout_test.md, reports/robustness.md and docs/MODEL_CARD.md in the repository for full evidence.')
        hosting_note='This is a shared public demo; hosting logs and browser caches are outside the app’s cleanup control.' if public_demo else 'This demo binds to localhost by default.'
        gr.Markdown('**Upload handling:** the application does not save uploads in its dataset or logs. Gradio uses temporary upload/preview files, with cleanup configured for files older than 60 seconds, checked every 30 seconds. Clearing resets the view; browser and hosting caches may persist. '+hosting_note,elem_classes='privacy-footer')
        button.click(analyze,inputs=[upload,review_session],outputs=[preview,state,indicators,feedback,detail],api_name='assess',concurrency_limit=1,concurrency_id='capture-processing')
        clear.click(clear_review,inputs=review_session,outputs=[upload,preview,state,indicators,feedback,detail],api_name=False,queue=False)
        upload.change(reset_review,inputs=[upload,review_session],outputs=[preview,state,indicators,feedback,detail],api_name=False,queue=False)
    return demo


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint-dir',default=os.environ.get('DERMREADY_CHECKPOINT_DIR',str(ROOT/'checkpoints')))
    p.add_argument('--model',choices=['cnn','quality_baseline'])
    p.add_argument('--host',default='127.0.0.1',help='Use 0.0.0.0 for a cloud web service')
    p.add_argument('--port',type=int,default=int(os.environ.get('PORT','7860')))
    args=p.parse_args();predictor=Predictor(args.checkpoint_dir,report_dir=ROOT/'reports',model_name=args.model)
    demo=build_app(predictor,public_demo=args.host not in ('127.0.0.1','localhost'))
    demo.launch(server_name=args.host,server_port=args.port,share=False,show_error=False,
                blocked_paths=[str((ROOT/'data').resolve()),str(Path(args.checkpoint_dir).resolve()),str((ROOT/'.env').resolve()),
                               str(ROOT/'quality_baseline.json'),str(ROOT/'decision_policy.json'),str(ROOT/'best.pt')],
                max_file_size='20mb',run_history=False,enable_monitoring=False,mcp_server=False,
                theme=app_theme(),css=CSS,footer_links=[])

if __name__=='__main__':main()

