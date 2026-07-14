# Full-Stack Core

> *This directory holds the full technical documentation for Full-Stack Core. This file serves as its entry point: it gives a high-level overview of the application, then points to the file covering each layer of the system, from the technology stack to the runtime behavior of key user-facing flows.*

## I. Project Overview

Full-Stack Core is a monolithic server-side rendered web application that presents a demo AI inference platform. Visitors register, submit text prompts, and receive generated responses through their personal workspace. A public collaboration form captures inbound leads, while moderators review those requests and administrators manage user accounts.

| Capability | Description |
|---|---|
| Session-based authentication | Login and registration establish a server-side session stored in Redis; protected routes read the session cookie on each request and reject unauthenticated access before handler logic runs. |
| Role-based access control | Users carry a role (USER, MODERATOR, or ADMIN) that determines which pages and actions are available; administrative surfaces enforce role checks before rendering or mutating data. |
| Server-side rendering | Pages are composed on the server as typed HTML components and returned as complete documents, keeping business logic and presentation colocated in Python modules. |
| HTMX partial updates | Form submissions and inline actions return HTML fragments that HTMX swaps into the existing DOM, enabling validation feedback and list updates without a full page reload. |
| Background inference | Text generation is offloaded to a dedicated GPU worker via Celery and runs concurrently with the web server; the handler enqueues the task and surfaces results through polling partials in the inference UI and a paginated history page. |
| IP-based rate limiting | A sliding-window counter in Redis rejects requests from an IP that exceeds the configured threshold before any route logic runs. |
| Access logging | Every request/response pair is logged with method, path, status code, and latency. |
| Uniform error handling | Expected HTTP exceptions and unhandled failures are mapped to consistent HTML error responses suitable for both full-page renders and HTMX swaps. |

## II. Documentation Overview

Each file focuses on a specific layer of abstraction, ranging from the technology stack to the runtime behavior of individual user flows.

- To review the runtime dependencies, infrastructure services, and technology stack, see  
    [01-dependencies.md](01-dependencies.md).

- To understand the repository layout, package boundaries, and codebase organization, see  
    [02-project-structure.md](02-project-structure.md).

- To review runtime interaction patterns and sequence diagrams for key user flows, see  
    [03-user-flows.md](03-user-flows.md).