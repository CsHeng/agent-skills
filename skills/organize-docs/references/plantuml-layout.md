# PlantUML Layout

Read this when a PlantUML diagram is crowded, labels or edges overlap, the reading path is unclear, or the rendered output is hard to read at normal zoom.

## Principle

Reduce visual density through structure first, then use styling to clarify the structure that remains. When many edges cross or labels overlap, simplify the graph model before tuning layout.

## Workflow

1. Establish the current render state: validate with `plantuml --check-syntax`, render PNG or SVG into a per-run directory under `$TMPDIR`, and inspect the rendered image alongside the source.
2. Choose the primary reading path the reader should follow first. Group secondary details into packages, notes, legends, or collapsed nodes, and keep only the edges that explain the diagram's purpose on the main canvas.
3. Reduce structure before styling. Replace all-to-all connections with an aggregate node such as an overlay, bus, entrypoint, control plane, policy group, or backend group; collapse internal components that only add edge density; keep one main flow direction; use hidden edges sparingly to stabilize ranks after the model is simplified.
4. Move explanations out of edges. Keep edge labels to one to three words, put long conditions and operational detail in node text, notes, or legends, use a legend for repeated semantics such as colors, client classes, route types, or failure modes, and use a note for a local caveat best expressed outside a node.
5. Apply minimal style after the structure reads well. Pick `left to right direction` or top-down according to the primary path, tune `nodesep`, `ranksep`, and `wrapWidth` after reducing edge count, and give color a semantic meaning such as ownership or layer. `skinparam linetype ortho` can create label collisions, so keep it only when the rendered image improves.
6. Re-validate and re-render after the final edit. Check for text crossing boxes, labels sitting on arrows, compressed packages, excessive blank space, and extreme aspect ratios, and iterate until the image is readable at normal zoom.

## Commands

```bash
out="$(mktemp -d "${TMPDIR:-/tmp}/puml-render.XXXXXX")"
plantuml --check-syntax path/to/diagram.puml
plantuml -tsvg -o "$out" path/to/diagram.puml
```

Rendered PNG or SVG output stays outside the repository unless the user asks for generated artifacts or the repository declares an owned projection.
