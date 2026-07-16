import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import "./ForgeLayout.css";

interface ForgeLayoutProps {
  library?: ReactNode;
  toolbar?: ReactNode;
  footer?: ReactNode;
  libraryLabel?: string;
  canvasLabel?: string;
  className?: string;
}

export default function ForgeLayout({
  library,
  toolbar,
  footer,
  libraryLabel = "Forge library",
  canvasLabel = "Forge canvas",
  className = "",
  children,
}: PropsWithChildren<ForgeLayoutProps>) {
  return (
    <div
      className={[
        "forge-layout",
        library
          ? "forge-layout-with-library"
          : "forge-layout-canvas-only",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {library && (
        <aside
          className="forge-layout-library"
          aria-label={libraryLabel}
        >
          {library}
        </aside>
      )}

      <section
        className="forge-layout-workspace"
        aria-label={canvasLabel}
      >
        {toolbar && (
          <header className="forge-layout-toolbar">
            {toolbar}
          </header>
        )}

        <main className="forge-layout-canvas">
          {children}
        </main>

        {footer && (
          <footer className="forge-layout-footer">
            {footer}
          </footer>
        )}
      </section>
    </div>
  );
}
