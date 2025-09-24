import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "AutoHire Candidate Portal",
  description: "Candidate experience for the AutoHire marketplace"
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
