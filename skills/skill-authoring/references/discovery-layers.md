# Discovery Layers

A Skill's facts reach the model through layers that become visible at different moments. Put each fact where it is visible when the model uses it, and let each lower layer refine the one above without contradicting it. When two layers disagree, fix the summary instead of adding an exception in a third place.

| Layer | Visible | Holds | Does not hold |
| --- | --- | --- | --- |
| Catalog entry | Every turn, before selection | Name and description: the decision the Skill resolves, its trigger, the one or two most confusable exclusions with receivers, an explicit or overlay marker | Method steps, full neighbor lists, keyword lists, examples |
| Router and scope contracts | When ownership is ambiguous or a method must be chosen | Clusters of neighbors, the question that separates them, handoffs with one receiver each, session-level selection rules | A Skill's own method or admission details |
| Body admission | After selection | When the Skill applies, what it refuses with the receiver for each refusal, the authority it needs | Another copy of the neighbor registry |
| Body procedure and references | After selection; a reference only when the body points to it | Method, decision detail, examples needed to execute | Admission conditions, because a reference loads too late to stop a wrong selection |
| Host metadata | Depends on the host | Machine projections of the activation mode, such as an implicit-invocation policy | Meaning that the portable text does not already carry |
| Maintenance | Only while maintaining | Inventory, activation registry, checks, diagrams, rationale, paired probes | Anything the model must know at run time |

## Activation Modes

Use host-neutral activation semantics and let each host project them:

- native: any matching request may select the Skill;
- conditional: the Skill overlays the primary owner while its boundary is active;
- baseline: the Skill always participates in composition;
- composition: the Skill loads only through a named composer;
- explicit: the Skill loads only when the user names it or explicitly asks for its workflow.

Carry every mode in portable text first. A host mechanism may enforce, restore, or present that meaning, but it must not be the only carrier, because other hosts and child agents may not see it.

- An implicit-invocation policy in host metadata enforces composition and explicit modes where the host supports it. Elsewhere, an explicit Skill needs a description marker and a body guard that stops when the user did not name or request it.
- Mention syntax differs between hosts; describe the triggering request in words rather than relying on one host's syntax.
- A shared frontmatter flag that disables model invocation can make a Skill loadable only through a command, so a user who names it in natural language may no longer reach it. Prefer a description marker and body guard unless every target host's behavior is verified.

## Invocation Surface

- Model-invoked Skills spend context through their name and description every session. Use them only when the agent should select the Skill without the user naming it.
- User-invoked Skills reduce prompt competition but require the user or a router to remember them.
- Keep overlapping third-party workflow libraries out of the default discovery surface unless their descriptions are curated and duplicate public IDs or ambiguous ownership are ruled out.
- Prefer a small router for session defaults over exposing many broad workflow descriptions.
- A host-level entry instruction may point at the router and state its bypass rules. It must not redefine a Skill's meaning, list install paths, or grant authority.

## Description Quality

- Put trigger conditions in the description, not only in the body.
- Keep it specific enough to select and narrow enough not to take unrelated tasks.
- Name the receiver of each exclusion it keeps, and drop exclusions that no model would confuse.
- Avoid synonyms that describe the same trigger branch, and keyword lists that act as a second router.
- Mark retired, experimental, explicit, or overlay Skills so they do not compete with active model-selected Skills.
