"""Local assets and responsive styling for the capture-review interface."""

HERO = '''
<section class="derm-hero" aria-label="DermReady introduction">
  <div class="hero-top"><span class="brand-mark" aria-hidden="true">◉</span>
    <span class="brand-name">DermReady<span class="brand-dot">.</span></span>
    <span class="research-pill">RESEARCH PROTOTYPE</span></div>
  <div class="hero-copy"><span class="eyebrow">A LITTLE CLARITY BEFORE YOU SEND</span>
    <h1>A clearer capture.<br><span>A better starting point.</span></h1>
    <p>Explore your photograph’s capture quality, find a practical next step,
    and compare a new capture — all in one place.</p></div>
  <div class="hero-art" aria-hidden="true"><div class="viewfinder">
    <span class="focus-ring"></span><span class="finder-label">FOCUS · LIGHT · DETAIL</span>
    </div><span class="art-caption">Keep the original. See what changes.</span></div>
</section>
<div class="journey" aria-label="Capture review steps">
  <div><span class="step-number">01</span><strong>Check your capture</strong><small>Explore focus, light and detail</small></div>
  <div><span class="step-number">02</span><strong>Find your next step</strong><small>Get practical capture guidance</small></div>
  <div><span class="step-number">03</span><strong>Compare a retake</strong><small>See what changed, side by side</small></div>
</div>
'''

CSS = '''
.gradio-container {width:100% !important; min-width:0 !important; max-width: 1180px !important; margin: auto !important;
  padding: 28px 24px 48px !important; font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;}
body {background: #ffffff;}
.gradio-container > .main {padding:0 !important; width:100% !important; min-width:0 !important;}
.gradio-container .main > .wrap {padding:0 !important; width:100% !important; min-width:0 !important;}
.derm-hero {position: relative; overflow: hidden; background: #102f36;
  border-radius: 26px; padding: 30px 38px 42px; color: #f7faf6; margin-bottom: 20px;}
.hero-top {display:flex; align-items:center; gap:12px;}
.brand-mark {display:grid; place-items:center; width:36px; height:36px; border:1px solid #72978e;
  border-radius:12px; color:#b9e4c8; font-size:25px;}
.brand-name {font-size:24px; font-weight:750; letter-spacing:-1px; color:#f7faf6 !important;}
.brand-dot {color:#c6eda5;}
.research-pill {margin-left:auto; border:1px solid #54777c; padding:7px 11px;
  border-radius:30px; font-size:10px; letter-spacing:1.5px; color:#d4e3df;}
.hero-copy {max-width:640px; margin-top:38px; position:relative; z-index:1;}
.eyebrow {font-size:10px; letter-spacing:2px; color:#b9d0c9; font-weight:650;}
.derm-hero h1 {font-size:clamp(32px,4.4vw,54px); line-height:1.12; letter-spacing:-2px;
  font-weight:650; margin:14px 0 18px; color:#fff;}
.derm-hero h1 span {color:#c6eda5;}
.hero-copy p {font-size:15px; line-height:1.7; max-width:480px; color:#c9dcd7; margin:0;}
.hero-art {position:absolute; right:55px; top:120px; width:240px; text-align:center;}
.viewfinder {height:170px; border:1px solid #52787b; border-radius:22px; display:grid;
  place-items:center; background:radial-gradient(ellipse at center,#365b57,#173b40 75%);
  box-shadow:0 0 0 12px #ffffff04; transform:rotate(-6deg); position:relative;}
.focus-ring {width:70px; height:70px; border:1px solid #bfe59f; border-radius:50%;
  box-shadow:0 0 0 14px #bfe59f12,0 0 0 32px #bfe59f07;}
.finder-label {position:absolute; bottom:17px; font-size:8px; letter-spacing:2px; color:#d1e0d2;}
.art-caption {display:block; font-size:10px; color:#a6c4bc; margin-top:24px;}
.journey {display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:18px;}
.journey>div {background:#fff; padding:18px; border:1px solid #dce5df; border-radius:16px;
  display:grid; grid-template-columns:34px 1fr; column-gap:10px; align-items:center;}
.step-number {grid-row:span 2; font-size:12px; color:#2d6552; background:#edf4eb;
  border-radius:10px; padding:10px 7px; font-weight:700;}
.journey strong {font-size:13px; color:#183c37;}
.journey small {font-size:11px; color:#677b72; margin-top:4px;}
#mode-banner {font-size:12px; padding:6px 4px; color:var(--body-text-color-subdued);}
.capture-card {border:1px solid var(--border-color-primary) !important; border-radius:20px !important;
  background:var(--block-background-fill) !important; padding:22px !important;}
.section-heading h3 {font-size:19px !important; letter-spacing:-.5px; margin:0 0 5px !important;}
.section-heading p {font-size:13px; color:var(--body-text-color-subdued);}
#capture-upload {min-height:180px; border-radius:14px;}
.primary-action {min-height:48px; border-radius:12px !important; font-weight:650 !important;}
#assessment textarea {font-size:21px !important; font-weight:650; color:var(--body-text-color);}
#assessment {border-left:4px solid #518771 !important;}
#capture-preview {min-height:280px;}
.tabs {margin-top:14px;}
.tab-nav button {padding:12px 20px !important; font-weight:600 !important; font-size:14px !important;}
.tab-nav button.selected {color:var(--button-primary-text-color) !important;
  background:var(--button-primary-background-fill) !important; border-radius:10px 10px 0 0 !important;}
.comparison-heading {padding:12px 0;}
.privacy-footer {font-size:11px !important; color:var(--body-text-color-subdued); line-height:1.7;
  padding-top:18px !important; border-top:1px solid var(--border-color-primary); margin-top:16px;}
@media(max-width:850px) {.hero-art {display:none;} .hero-copy {max-width:100%;}}
@media(max-width:600px) {
  .gradio-container {padding:12px 10px 28px !important;} .derm-hero {padding:24px; border-radius:18px;}
  .hero-copy {margin-top:26px;} .derm-hero h1 {letter-spacing:-1px;}
  .research-pill {font-size:8px; letter-spacing:.5px; padding:6px 8px;}
  .hero-top {flex-wrap:wrap;} .brand-name {font-size:21px;}
  .research-pill {margin-left:0;}
  .derm-hero h1 {font-size:32px;}
  .tab-nav {flex-wrap:wrap !important;}
  .insights-row {flex-direction:column !important;}
  .journey {grid-template-columns:1fr; gap:8px;} .journey>div {padding:12px;}
  .capture-card {padding:15px !important;} .tab-nav button {padding:10px 12px !important;}
}
/* Reference light palette and accessible tab states across Gradio markup. */
.gradio-container {
  --body-background-fill:#ffffff;
  --block-background-fill:#ffffff;
  --body-text-color:#202c40;
  --body-text-color-subdued:#71869a;
  --border-color-primary:#dce5ee;
  background:#ffffff !important; color:#202c40; box-sizing:border-box;
}
.gradio-container [role="tablist"] {
  display:flex; flex-wrap:wrap; gap:4px; border-bottom:1px solid #dce5ee;
}
.gradio-container [role="tab"] {
  border-radius:0 !important; background:transparent !important;
  color:#202c40 !important; border-bottom:2px solid transparent !important;
  padding:12px 16px !important;
}
.gradio-container [role="tab"][aria-selected="true"] {
  color:#00a99c !important; background:transparent !important;
  border-bottom-color:#00b9ab !important;
}
.gradio-container button:focus-visible {
  outline:3px solid #82dacf !important; outline-offset:3px;
}
.gradio-container .capture-card {min-width:0 !important;}
.gradio-container #capture-preview {height:326px;}
.gradio-container .privacy-footer {overflow-wrap:anywhere;}
@media(max-width:600px) {
  .gradio-container [role="tab"] {font-size:12px !important; padding:10px 9px !important;}
  .gradio-container #capture-preview {height:260px;}
}

/* Readable review text and tables at ordinary desktop zoom. */
.gradio-container {font-size:15px !important;}
.gradio-container .prose p, .gradio-container .prose li {font-size:14px !important; line-height:1.65;}
.gradio-container textarea, .gradio-container table {font-size:14px !important; line-height:1.6;}
.gradio-container .section-heading p {font-size:14px !important;}
.gradio-container .privacy-footer {font-size:12px !important;}

'''


def app_theme():
    import gradio as gr
    return gr.themes.Soft(primary_hue='teal', neutral_hue='slate',
                          font=['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif']).set(
        button_primary_background_fill='#245b4b',
        button_primary_background_fill_hover='#174536',
        button_primary_text_color='#ffffff',
        button_primary_background_fill_dark='#245b4b',
        button_primary_background_fill_hover_dark='#174536',
        button_primary_text_color_dark='#ffffff',
        block_radius='16px',
    )
