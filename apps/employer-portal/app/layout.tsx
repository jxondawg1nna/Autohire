import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "AutoHire Employer Portal",
  description: "Employer and recruiter experience for AutoHire"
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
