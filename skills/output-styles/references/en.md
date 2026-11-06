# English Reply Patterns

Read this when the reply is in English. The body of `output-styles` owns the method; this reference maps it to the countable rules of ASD-STE100 Simplified Technical English (Issue 9) and lists the common filler patterns. The mapping borrows rules, not the dictionary, so a reply never claims STE compliance.

## Countable Rules Borrowed From ASD-STE100

| Rule (Issue 9) | What the reply does |
| --- | --- |
| 5.1 | An instruction sentence has at most 20 words. |
| 5.2 | One instruction per sentence, unless two actions happen at the same time. |
| 6.3 | A descriptive sentence has at most 25 words. |
| 6.6 | A descriptive paragraph has at most six sentences. |
| 2.1 | A compound noun has at most three nouns. |
| 3.6 | Active voice; passive only when the actor is unknown. |
| 4.2 | No contractions in instructions, and no words dropped to shorten a sentence. |
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

Delete process narration ("first I looked at the config, then I...") and write the finding with its evidence.

## Hedges

- A fact that is not confirmed is written as unconfirmed with the check that would confirm it, not softened with "should be fine" or "probably works".
- "May" and "possibly" stay when they state a real likelihood and carry their basis: "the cache may be the cause, because only the EU nodes set `CACHE_TTL=900`".
- "Not verified" stays "not verified"; it does not become "works".

## Modals

Use one modal per strength: must for a requirement, must not for a prohibition, may for permission, should only for a recommendation the user may decline. Quote a source's own modal verbatim when citing it.
