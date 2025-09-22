# Employer Portal

The employer portal is a Next.js 14 application that powers organization and recruiter workflows for AutoHire. It will eventually deliver job posting, applicant pipeline management, sourcing, microtask campaigns, and ATS synchronization.

## Development

```bash
npm install
npm run dev
```

Environment variables should be stored in `.env.local`; see `.env.example` for required keys.

## Architecture Notes

- Uses the App Router with server components where possible.
- Integrates with the FastAPI backend for job, application, and microtask APIs.
- Authenticates with Keycloak leveraging organization-scoped roles.
- Will share UI primitives via a dedicated design system package.

