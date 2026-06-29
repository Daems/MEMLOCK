# Nano Banana Pro Automation Skill

Use this skill when creating or operating image-generation workflows through Kie.ai Nano Banana Pro.

## Inputs

- `prompt`: required image instruction.
- `image_input`: optional public image URLs for reference or transformation.
- `aspect_ratio`: one of `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `auto`.
- `resolution`: `1K`, `2K`, or `4K`.
- `output_format`: `png` or `jpg`.

## Procedure

1. Check that `KIE_API_KEY` is present in the environment.
2. Validate prompt, aspect ratio, resolution, and output format.
3. Submit a task to `POST /api/v1/jobs/createTask` with `model: nano-banana-pro`.
4. Store the returned task ID.
5. Use callback mode when a public callback URL is available.
6. Otherwise poll the task record endpoint with exponential backoff.
7. When successful, parse result URLs and download them immediately.
8. Save task metadata and outputs.
9. Never expose API keys in frontend code or public repos.

## Failure handling

- On `401`, check bearer token and environment loading.
- On `429`, slow down submission rate and retry later.
- On `fail`, persist the full response and inspect `failCode` / `failMsg`.
- On missing result URLs, save the full response for inspection.
