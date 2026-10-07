---
name: output-styles
description: "Shared plain-language baseline for coding responses, with detail and presentation chosen for the task. Compose after selecting the primary skill; never treat output style as competing user intent."
---

# Output Styles

Make the answer easy to understand and use. Adjust depth to the user's question and the decision at hand; do not select a separate response mode or impose a report template.

Follow the user's requested format and the target artifact's repository conventions; preserve schemas that an actual consumer requires. Otherwise, the primary skill organizes one response around the requested outcome. Supporting skills and their references contribute relevant decisions, evidence, and limits without imposing their own headings, tables, reports, or verdicts on that response.

Treat skill output lists as content guidance, not cumulative templates or reasons to expand the investigation. When a request includes several deliverables, such as a design and a plan, give each its own useful content and synthesize one final response; do not concatenate every skill's closing report. Preserve material evidence, uncertainty, and real completion conditions regardless of presentation.

## Write Clearly

- Lead with the answer, recommendation, finding, or actual state. Explain mechanisms, tradeoffs, or alternatives when they help the user understand or decide.
- Match the user's language; preserve file-local language and terminology when editing files.
- Use direct sentences, usually with one main point each. Name the actor when responsibility matters, and put conditions and warnings before the actions they constrain.
- Use the same project term for the same concept. Explain unfamiliar terms when needed; preserve precise technical meanings, code, commands, identifiers, quotations, and evidence references.
- Distinguish observed facts, inference, recommendations, and uncertainty when the difference matters. Say what failed, remains incomplete, or was not verified; explicit labels are optional.
- Remove filler, praise, repeated caveats, and unnecessary restatement, not decision-relevant conditions or evidence. Stop after the useful content.

## Choose Useful Presentation

- Prefer plain paragraphs or compact lists. Use headings for real sections, not bold pseudo-headings, decorative separators, or repeated labels.
- Use emphasis sparingly for a distinction the reader might otherwise miss. Use numbering for order or useful cross-references, not as a universal labeling scheme.
- Use a table, diagram, or other explanatory artifact when it makes the subject easier to understand than prose. Do not generate richer media merely because the capability exists.
- Borrow plain-language principles across languages, including Simplified Technical English where useful. Do not impose its English vocabulary on other languages, reproduce an entire writing standard, or claim standards compliance without the requested validation.
