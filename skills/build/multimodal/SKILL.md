---
name: multimodal
description: Design an agent's handling of non-text inputs and outputs — images, documents/PDFs, audio — including preprocessing, token/cost budgeting, grounding on visual evidence, and failure modes specific to each modality. Use when an agent ingests images/PDFs/audio, when multimodal input is slow or expensive, or when the agent misreads visual content.
---

# Multimodal Handling

Non-text inputs break assumptions text-only agents rely on: an image can cost thousands of tokens, a scanned PDF can be unreadable, audio needs transcription with its own errors. This skill designs how modalities enter and leave the agent — preprocessing, budgeting, and modality-specific failure modes — so multimodal features are reliable and affordable.

## When to use
- An agent ingests images, screenshots, PDFs/documents, or audio.
- Multimodal input is slow, expensive, or blows the token budget.
- The agent misreads charts, tables, scans, or diagrams.

## When NOT to use
- The input is already clean text (or text extraction is trivially reliable) — treat it as text.
- Pure text agents — nothing here applies.

## Procedure

1. **Decide preprocess-vs-native per modality.** Some content the model should see natively (a photo, a chart to interpret); some should be *extracted to text first* (a text-heavy PDF, a table, a transcript) because extraction is cheaper, more reliable, and citable. Choosing "send the raw image" for a text document wastes tokens and loses fidelity. Route each modality to the cheaper reliable path.

2. **Budget tokens per modality — images are expensive.** A single high-res image can cost as much as pages of text, and cost scales with resolution. Downsample to the lowest resolution that preserves the needed detail; page-cap documents; chunk long audio. Measure the per-input token cost (`cost-optimization`, `context-engineering`) — multimodal is where token budgets silently blow up.

3. **Handle degraded inputs explicitly.** Real inputs are rotated, blurry, low-contrast, partially cut off, or scanned. Define behavior: preprocess to improve (deskew, upscale, OCR) where possible, and have the agent flag "can't read this clearly" rather than confabulate. A confident answer from an unreadable scan is the core multimodal failure.

4. **Ground on the visual evidence.** When the agent reports what's *in* an image/document (a number from a chart, a clause from a contract), it should point to where — region, page, timestamp — so a human can verify (`grounding-citation`). Visual hallucination (misreading a value, inventing a table row) is hard to catch without this.

5. **Design multimodal output where relevant.** If the agent produces images, documents, or charts, decide the generation path and how outputs are returned and verified. Verify generated artifacts (does the chart show the right numbers?) rather than trusting them.

6. **Test on real messy inputs.** Evaluate on the actual distribution — phone photos, real scans, real recordings — not clean samples. Add eval cases for the degraded-input and visual-hallucination failure modes (`eval-harness`). Multimodal accuracy on clean test images tells you nothing about production.

## Output contract
A multimodal design: per-modality preprocess-vs-native routing, token/resolution budget with measured per-input cost, degraded-input handling, visual grounding to region/page/timestamp, output-generation + verification path if applicable, and eval cases on realistic messy inputs.

## Checklist
- [ ] Each modality routed to the cheaper reliable path (native vs. extract-to-text).
- [ ] Per-input token cost measured; resolution/page/length budgeted.
- [ ] Degraded inputs handled (preprocess or flag), not confabulated.
- [ ] Visual claims grounded to a verifiable location.
- [ ] Generated artifacts verified, not trusted.
- [ ] Evaluated on realistic messy inputs, with degraded/visual-hallucination cases.
