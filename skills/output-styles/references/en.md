# English Reply Patterns

Read this when the reply is in English. The body of `output-styles` owns the method; this reference maps it to the countable rules of ASD-STE100 Simplified Technical English (Issue 9) and lists the common filler patterns and the contrast rewrite. The mapping borrows the countable rules only; the dictionary stays out, so a reply describes its own content in the user's terms.

## Countable Rules Borrowed From ASD-STE100

| Rule (Issue 9) | What the reply does |
| --- | --- |
| 5.1 | An instruction sentence has at most 20 words. |
| 5.2 | One instruction per sentence, unless two actions happen at the same time. |
| 6.3 | A descriptive sentence has at most 25 words. |
| 6.6 | A descriptive paragraph has at most six sentences. |
| 2.1 | A compound noun has at most three nouns. |
| 3.6 | Active voice; passive only when the actor is unknown. |
| 4.2 | Full words in instructions: every word a sentence needs stays in it. |
| 8.1 | Any standard punctuation except the semicolon between clauses. |

Rules 1.2 and 1.3 (approved words with one meaning and one part of speech) are the dictionary part. A reply applies their intent through the user's and the project's terms, one term per concept.

## Filler And Nominalization

| Pattern | Direct form |
| --- | --- |
| perform a modification of, carry out a check of | modify, check |
| in order to, for the purpose of | to |
| prior to, subsequent to | before, after |
| it is imperative that X | X must |
| it is worth noting that, it should be noted that | (delete; write the note) |
| leverage, utilize | use |
| a number of, a certain amount of | the actual number, or delete |
| going forward, at this point in time | now, or delete |
| the fact that X | X |
| first I looked at the config, then I... | the finding with its evidence |

## Contrast

State what a thing is and let the claim stand on its evidence. Add what it is not only when the user or the evidence shows that misreading, after the positive statement and at most once per topic. A chain of "this does not mean / nor does it / let alone" clauses becomes the positive statements it was guarding, or is cut.

| Before | After |
| --- | --- |
| The health check is not just a process check, which is a strength. It checks the unit, the API, the TUN, then DNS and an HTTPS 204. | The health check covers the unit, the API, the TUN, then DNS and an HTTPS 204. |
| Gateway health does not mean every business selector works, nor that the Internet is reachable, let alone that the proxy chain is healthy. | Gateway health proves the top-level `Proxy` path; each business selector gets its own probe. |
| This is a development input, not a production dependency. | The workspace contract is a development input; production reads the published schema. |

## Hedges

- An unconfirmed fact is written as unconfirmed with the check that would confirm it.
- "May" and "possibly" stay when they state a real likelihood and carry their basis: "the cache may be the cause, because only the EU nodes set `CACHE_TTL=900`".
- A check that was skipped is reported as skipped, with its reason, in one closing line.

## Modals

Use one modal per strength: must for a requirement, must not for a prohibition, may for permission, should only for a recommendation the user may decline. Quote a source's own modal verbatim when citing it.
