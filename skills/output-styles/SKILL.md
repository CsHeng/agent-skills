---
name: output-styles
description: "Shared plain-language baseline for coding responses, with detail and presentation chosen for the task. Compose after selecting the primary skill; never treat output style as competing user intent."
---

# Output Styles

Make the answer easy to understand and use. Follow the user's presentation preferences and use the detail the decision needs. Persistent preferences live in always-loaded user or host instructions; this Skill supplies writing methods.

Follow the user's requested format and the target artifact's repository conventions, and keep schemas that an actual consumer requires. Otherwise, the primary skill organizes one response around the requested outcome. Supporting skills and their references contribute relevant decisions, evidence, and limits within the primary response's own structure.

Use each skill's output list as content for the one primary response, within the requested investigation. When a request includes several deliverables, such as a design and a plan, give each its own useful content and synthesize one final response. Keep material evidence, uncertainty, and real completion conditions in whatever presentation you choose.

## Write Clearly

- Lead with the answer, recommendation, finding, or actual state. Explain mechanisms, tradeoffs, or alternatives when they help the user understand or decide.
- Match the user's language; keep file-local language and terminology when editing files.
- Use direct sentences, usually with one main point each. Name the actor when responsibility matters, and put conditions and warnings before the actions they constrain.
- Use the same project term for the same concept. Explain unfamiliar terms when needed, and keep precise technical meanings, code, commands, identifiers, quotations, and evidence references intact.
- Distinguish observed facts, inference, recommendations, and uncertainty when the difference matters, and say what failed, remains incomplete, or was not verified. Explicit labels are optional.
- Keep decision-relevant conditions and evidence; cut filler, praise, repeated caveats, and restatement; end when the useful content is done.

## Choose Useful Presentation

- Use plain paragraphs or compact lists, with headings for real sections and plain text elsewhere.
- Use emphasis sparingly, for a distinction the reader might otherwise miss.
- Add a table, diagram, or other explanatory artifact when it explains the subject better than prose.
- Apply plain-language principles (Simplified Technical English where the user asks for it) in the user's language; claim standards compliance only after requested validation.
- When the user needs to reply to or track items individually, print a short complete ASCII ID on each item, such as `- 5.1 Update project configuration` under existing item `5`, and keep the user's established references when updating those items. The user's global instructions own the full item-ID preference.
