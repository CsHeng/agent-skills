# Circuit Breaking, Load Shedding, And Health

Read this when the boundary calls a remote dependency or declares health or readiness endpoints.

## Circuit Breaking And Load Shedding

Use a circuit breaker when repeated dependency calls demonstrably amplify latency or resource exhaustion and the caller has meaningful open, half-open, and recovery behavior. Use concurrency limits, queues, or load shedding when the actual constraint is local capacity.

## Health And Readiness Evidence

Health checks answer an actor's decision. Liveness proves the process can make progress; readiness proves it can safely receive the declared work; dependency health and degraded-state evidence stay separate when their recovery actions differ. Make readiness exercise the dependency and resources the declared work needs.
