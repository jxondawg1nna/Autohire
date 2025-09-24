import { notFound } from "next/navigation";

import { fetchEmployer } from "@/lib/api";
import { DEMO_EMPLOYER_ID, DEMO_USER_ID } from "@/lib/config";
import { EMPLOYER_ROLE_LABELS, type Employer, type EmployerMember, type EmployerRole } from "@/lib/types";

export type EmployerContext = {
  employer: Employer;
  member: EmployerMember;
};

export function formatRoles(roles: EmployerRole[]): string {
  return roles.map((role) => EMPLOYER_ROLE_LABELS[role]).join(", ");
}

export async function requireEmployerRole(requiredRoles: EmployerRole[] = []): Promise<EmployerContext> {
  const employer = await fetchEmployer(DEMO_EMPLOYER_ID);
  const member = employer.members.find((entry) => entry.user_id === DEMO_USER_ID);

  if (!member) {
    notFound();
  }

  if (requiredRoles.length && !requiredRoles.some((role) => member.roles.includes(role))) {
    notFound();
  }

  return { employer, member };
}
