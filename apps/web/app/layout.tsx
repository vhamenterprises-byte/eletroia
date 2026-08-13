import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EletroIA",
  description: "Plataforma de IA para projetos elétricos residenciais",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
