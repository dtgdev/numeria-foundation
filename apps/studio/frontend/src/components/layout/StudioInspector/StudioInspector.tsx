import type { PropsWithChildren, ReactNode } from "react";

import "./StudioInspector.css";

interface StudioInspectorProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export default function StudioInspector({
  title,
  description,
  actions,
  children,
}: PropsWithChildren<StudioInspectorProps>) {
  return (
    <aside className="studio-inspector">
      <header className="studio-inspector-header">
        <div>
          <p className="studio-inspector-eyebrow">
            INSPECTOR
          </p>

          <h2>{title}</h2>

          {description && <p>{description}</p>}
        </div>
      </header>

      <div className="studio-inspector-content">
        {children}
      </div>

      {actions && (
        <footer className="studio-inspector-actions">
          {actions}
        </footer>
      )}
    </aside>
  );
}
