# Discovery Layers

A Skill's facts reach the model through layers that become visible at different moments. Put each fact where it is visible when the model uses it, and let each lower layer consistently refine the one above. When two layers disagree, fix the summary.

| Layer | Visible | Holds | Owned elsewhere |
| --- | --- | --- | --- |
| Catalog entry | Every turn, before selection | Name and description: the decision the Skill resolves, its trigger, the one or two most confusable exclusions with receivers, an explicit or overlay marker | Method steps, full neighbor lists, keyword lists, examples |
| Router and scope contracts | When ownership is ambiguous or a method must be chosen | Clusters of neighbors, the question that separates them, handoffs with one receiver each, session-level selection rules | A Skill's own method or admission details |
| Body admission | After selection | When the Skill applies, what it refuses with the receiver for each refusal, the authority it needs | Another copy of the neighbor registry |
| Body procedure and references | After selection; a reference only when the body points to it | Method, decision detail, examples needed to execute | Admission conditions, because a reference loads too late to stop a wrong selection |
| Host metadata | Depends on the host | Machine projections of the activation mode, such as an implicit-invocation policy | Meaning carried by portable text |
| Maintenance | Only while maintaining | Inventory, activation registry, checks, diagrams, rationale, paired probes | Anything the model must know at run time |

## Activation Modes

Use host-neutral activation semantics and let each host project them:

- native: any matching request may select the Skill;
- conditional: the Skill overlays the primary owner while its boundary is active;
- baseline: the Skill always participates in composition;
- composition: the Skill loads only through a named composer;
- explicit: the Skill loads only when the user names it or explicitly asks for its workflow.

Carry every mode in portable text first so other hosts and child agents can see it. A host mechanism may enforce, restore, or present that meaning.

- An implicit-invocation policy in host metadata enforces composition and explicit modes where the host supports it. Elsewhere, an explicit Skill needs a description marker and a body guard that proceeds only when the user names or requests it.
- Mention syntax differs between hosts; describe the triggering request in host-neutral words.
- A shared frontmatter flag that disables model invocation can make a Skill loadable only through a command, so a user who names it in natural language may lose access. Prefer a description marker and body guard unless every target host's behavior is verified.

## Invocation Surface

- Model-invoked Skills spend context through their name and description every session. Use them when the agent should select the Skill independently of an explicit user request.
- User-invoked Skills reduce prompt competition but require the user or a router to remember them.
- Keep overlapping third-party workflow libraries out of the default discovery surface unless their descriptions are curated and duplicate public IDs or ambiguous ownership are ruled out.
- Prefer a small router for session defaults over exposing many broad workflow descriptions.
- A host-level entry instruction may point at the router and state its bypass rules. The Skill owns its meaning, installation guidance owns install paths, and approved scope owns authority.

## Description Quality

- Put trigger conditions in the description.
- Keep it specific enough to select and narrow enough to admit only relevant tasks.
- Name the receiver of each exclusion it keeps, and keep exclusions for plausible confusion.
- Describe each trigger branch once; the router owns routing.
- Mark retired, experimental, explicit, or overlay Skills to distinguish them from active model-selected Skills.
