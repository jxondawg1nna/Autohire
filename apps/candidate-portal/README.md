# Candidate Portal

The candidate portal is a Next.js 14 application that powers the talent experience for AutoHire. It will eventually include onboarding flows, profile management, job discovery, microtasks, and automation controls.

## Development

```bash
npm install
npm run dev
```

Environment variables live in `.env.local`; an example template is provided in `.env.example`.

## Architecture Notes

- Uses the App Router and React Server Components.
- Communicates with the FastAPI backend via REST.
- Authenticates using Keycloak (OIDC) with PKCE.
- Shares UI primitives with other portals via a planned design system package.

