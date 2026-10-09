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
- Use emphasis sparingly for a distinction the reader might otherwise miss. Give individually addressable items ordered ASCII IDs as described below; ordinary prose and supporting detail do not need universal labeling.
- Use a table, diagram, or other explanatory artifact when it makes the subject easier to understand than prose. Do not generate richer media merely because the capability exists.
- Borrow plain-language principles across languages, including Simplified Technical English where useful. Do not impose its English vocabulary on other languages, reproduce an entire writing standard, or claim standards compliance without the requested validation.

## Make Items Easy To Refer To

- Give questions, options, findings, or actions that need individual replies or tracking short, ordered ASCII IDs such as `1`, `2`, `3`, or grouped IDs such as `A1`, `A2`, `B1`, with nested IDs such as `D4.1` when needed. The purpose is unambiguous reference throughout the session, like task IDs in a plan, not decorative numbering or an ASCII-only answer; keep the prose in the user's language.
- Each distinct item keeps a unique ID across the session, not merely within a section or response. Continue the sequence for new items; distinct group prefixes may separate item sets, but do not reset a group's numbering in each round. Prefer simple labeled lines or lists; do not make the user type Chinese numerals, decorative symbols, heading text, or Markdown markers such as `###` to identify an item.
- Reuse existing task or finding IDs instead of inventing a second numbering system. Updates, reordering, filtering, resolution, or reopening do not change an item's ID; never recycle a closed item's ID for a new item. For example, after fixing `F1` and `F2` from findings `F1`–`F3`, keep the unresolved finding as `F3` and assign new findings `F4` and `F5`, rather than renumbering the remaining list.
- For a split or merge, use fresh IDs for newly distinct items and state their relationship to the prior IDs. In summaries or handoffs, preserve the IDs, current meanings and statuses needed for continuation, and enough sequence context to avoid reuse; do not repeat a full ledger in every reply. IDs preserve traceability without freezing the plan or changing authority.
- Before sending, check that an ID such as `B2` or `D4.1` still identifies the same single item across rounds. Headings may organize longer answers, ordinary bullets may carry non-addressable supporting detail, and authored documents retain their appropriate Markdown structure; a simple answer does not need IDs.
