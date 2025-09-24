import Link from "next/link";
import type { ReactNode } from "react";

import { formatRoles, requireEmployerRole } from "@/lib/auth";

const NAV_LINKS = [
  { href: "/org", label: "Organization setup" },
  { href: "/jobs/new", label: "Job creation" },
  { href: "/pipelines", label: "Pipeline management" },
  { href: "/microtasks", label: "Microtask campaigns" },
];

type PortalLayoutProps = {
  children: ReactNode;
};

export default async function PortalLayout({ children }: PortalLayoutProps) {
  const { employer, member } = await requireEmployerRole();

  const roleSummary = formatRoles(member.roles);

  return (
    <div className="portal-shell">
      <aside className="portal-nav">
        <div className="portal-profile">
          <p className="portal-employer">{employer.name}</p>
          <p className="portal-member">Signed in as {member.name}</p>
          <p className="portal-roles">Roles: {roleSummary}</p>
        </div>
        <nav className="portal-links">
          {NAV_LINKS.map((item) => (
            <Link key={item.href} href={item.href} className="portal-link">
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="portal-content">{children}</main>
    </div>
  );
}
