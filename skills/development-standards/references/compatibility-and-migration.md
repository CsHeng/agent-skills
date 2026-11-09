# Compatibility And Migration

Read this when a change touches a public or persisted contract, retained data, a wire format, an automation entry point, or replaces an implementation. Cutover sequencing and protections are owned by [Replacement And Cutover](replacement-and-cutover.md); migration benefit judgment for a language or platform move is owned by language selection in `skills-routing`.

- Add or keep compatibility behavior when a current public or persisted contract, interoperability requirement, approved migration policy, or retained-state need requires it. Name its owner, supported versions, evidence, retirement condition, and migration path.
- Preserve required consumer behavior. A library's default help wrapping, numeric representation, object identity, or undocumented parsing quirk becomes a promise only when an actual consumer depends on it; establish consumers before reproducing such behavior.
- Distinguish internal implementation freedom from caller-visible APIs, stored data, wire formats, automation entry points, and generated compatibility surfaces.
- Authorized disposable development state may be rebuilt or replaced in place. Retained existing data still needs migration evidence even when the runtime is rebuilt.
- Remove obsolete compatibility paths when their approved retirement condition is met; update affected producers, consumers, tests, generated surfaces, and stable docs together.
- A temporary mechanism that ships, affects users, or creates a continuing maintenance obligation needs an owner and a concrete retirement or replacement condition; handle a scratch script within the existing authorization.
