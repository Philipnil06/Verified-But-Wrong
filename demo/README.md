# Verified but Wrong Demo

Static React/Vite demo for hackathon submission. The app replays precomputed reproduction outcomes from repository artifacts to explain the verified-but-wrong failure mode in under a minute.

## Run locally

1. `cd demo`
2. `npm install`
3. `npm run dev`
4. Open the local Vite URL shown in the terminal.

## Build

1. `cd demo`
2. `npm install`
3. `npm run build`
4. Optional preview: `npm run preview`

## Repro note

This demo uses precomputed reproduction results from the repository.
It does not run Dafny in the browser and does not require a backend server.

## Deploy on Vercel

1. Push the repo to GitHub.
2. Go to Vercel.
3. Import the GitHub repo.
4. Set **Root Directory** to `demo`.
5. Set **Framework Preset** to `Vite`.
6. Set **Build Command** to `npm run build`.
7. Set **Output Directory** to `dist`.
8. Deploy.
9. Share the generated `.vercel.app` URL in the hackathon submission.