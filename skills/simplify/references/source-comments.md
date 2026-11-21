# Source Comments

Read this when the cleanup covers source comments, or when a project wants a gate that holds a cleaned surface.

## Inventory

Enumerate comments with the language's parser or tokenizer, or with the project's own scanner, across production code, tests, and fixtures. Comment-like text inside strings, regexes, fixture data, and heredocs is data. These stay with their owners: executable directives and shebangs, required legal notices, generated and vendored output, archived originals, and documentation a tool or caller consumes.

## Dispositions

Read each comment with its implementation, callers, and tests, and refer to it by its location before any edit.

| Class | Evidence | Action |
| --- | --- | --- |
| Tautology | The code already says it | Delete |
| Stale | The current code contradicts it, and tests or consumers support the code | Delete |
| Workaround | It justifies a concrete workaround whose consequence is still real and whose repair someone can act on | Record the repair in the project's issue convention with its owner, affected behavior, and completion check; delete once that record exists |
| Decision | It explains a non-obvious choice that reaches across modules and that a future maintainer still needs explained | Move the rationale, consequences, and reconsideration condition into the decision owner under the lifecycle in `organize-docs`, then delete; reuse a record that already covers it, and give several comments about one choice one record |
| Local reason | A maintainer editing this line needs a reason the code cannot show, such as the failure the obvious alternative causes | Keep it, reduced to that reason |

A workaround note with no remaining consequence, or a decision the code makes obvious, is a tautology or stale; a workaround that must stay is a local reason or a decision. When tests, consumers, or recorded intent support a comment over the code it contradicts, the code is the defect: keep the comment and report the finding. A decision whose reason appears only in the implementation enters the decision owner marked as inferred; a reason that matters at one line stays a local reason. When the issue or decision record cannot be written within this request's scope and authority, keep the comment and report why.

## Removal

Preserve source semantics: keep the token separators and line breaks the language needs, and check for tooling that reads comment text. Run the owning checks after each cohesive group.

## Holding The Result

A project that wants new comments to fail a check adds a ratchet under Quality Gates in `development-standards`: a baseline of allowed existing occurrences that only shrinks, or a set of cleared directories that only grows. The rule detects that a comment is present and cannot judge its value, so it carries a reviewed exception path for kept local reasons and the protected classes above. The scanner, baseline, and exceptions belong to the project.
