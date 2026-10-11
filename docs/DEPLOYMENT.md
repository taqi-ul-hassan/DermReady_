# Public hackathon deployment

The repository is prepared for a Render Python web service. render.yaml explicitly selects the free plan, requirements-web.txt installs the lightweight capture/JSON-baseline runtime, and app.py listens on 0.0.0.0 and Render's PORT when launched by the service. Local startup remains localhost by default.

## Publish through Render

Connect Render in ChatGPT so the service can be created in your account. Alternatively open https://render.com/deploy?repo=https://github.com/taqi-ul-hassan/DermReady_ and authorize the repository/Blueprint. Confirm the Free service shown by the Blueprint; no paid instance is selected in the configuration. Wait for the deployment's Live status and use the actual service URL that Render returns. A URL cannot be promised before provisioning succeeds.

Free services sleep after inactivity and can take time to wake. Open the app before judging. The free instance has limited memory/CPU; the runtime avoids importing PyTorch for indicator or baseline inference and serializes capture processing. This does not establish a load-tested production service.

## Enable the evaluated default baseline privately

The public repository has no trained artifacts. With no secret files the hosted app is an explicitly labeled indicator/comparison demo: every suitability result remains uncertain.

In the Render service's Environment section, add two **Secret Files** from your existing trained-artifact ZIP, preserving their exact contents:

- quality_baseline.json
- decision_policy.json

Render mounts secret files under /etc/secrets; the Blueprint sets DERMREADY_CHECKPOINT_DIR to that directory. Redeploy the service. Its current-mode label should become quality_baseline, and Evidence & limits should confirm that the active artifact hashes match the published evaluation. Do not put the artifact JSON into the public GitHub repository or invent model parameters. No SCIN images, case manifests or split files are needed for this demo.

The optional CNN is not included in requirements-web.txt; it requires the full dependencies and private best.pt, plus appropriately sized hosting. The default baseline uses exactly the same feature extraction, coefficients and frozen policy as the local app.

## Reviewer checks after publication

1. Open the returned public URL in a signed-out browser. Confirm the current mode.
2. Try synthetic_original.png and synthetic_blur.png; inspect measured indicators.
3. Compare the two targets; explain that these are synthetic illustrations, not a clinical retake evaluation.
4. Try synthetic_noise.png and review the uncertainty explanation.
5. Open Evidence & limits and inspect artifact provenance and historical coverage/error rates.

The app is a public research demo: use synthetic or permitted non-identifiable examples. Gradio creates temporary files with periodic cleanup; hosting logs and browser caches are not covered by that cleanup. The app blocks serving private data, secret artifact directories and .env, disables analytics/run history and retains no upload records in its dataset. These application settings are not a guarantee of anonymous or instant-deletion hosting.

Official hosting references: https://render.com/docs/blueprint-spec, https://render.com/docs/web-services, https://render.com/docs/free and https://render.com/docs/configure-environment-variables.

## Verified readiness

The lightweight runtime passed 27 targeted regression checks and live synthetic upload/comparison/private-file tests. The actual cloud-mode entry point passed host/PORT startup and private-path checks. Full Linux, full Windows and lightweight-runtime CI all passed for commit 73498d320d48159631677c27c737f8ad308afbb9. See reports/cloud_deployment_checks.json for the run link. No public service has been provisioned yet: the Render account is not connected, and no public URL is verified.
