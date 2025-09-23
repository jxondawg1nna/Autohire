import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "AutoHire Admin Console",
  description: "Administrative controls for the AutoHire platform"
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
