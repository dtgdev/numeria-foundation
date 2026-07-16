import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import "./StudioInspector.css";

export interface InspectorSectionProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function InspectorSection({
  title,
  description,
  action,
  children,
}: PropsWithChildren<InspectorSectionProps>) {
  return (
    <section className="entity-inspector-section">
      <header className="entity-inspector-section-header">
        <div>
          <h3>{title}</h3>

          {description && (
            <p>{description}</p>
          )}
        </div>

        {action && (
          <div className="entity-inspector-section-action">
            {action}
          </div>
        )}
      </header>

      <div className="entity-inspector-section-content">
        {children}
      </div>
    </section>
  );
}

interface StudioInspectorProps {
  title: string;
  description?: string;
  eyebrow?: string;
  status?: ReactNode;
  actions?: ReactNode;
}

export default function StudioInspector({
  title,
  description,
  eyebrow = "INSPECTOR",
  status,
  actions,
  children,
}: PropsWithChildren<StudioInspectorProps>) {
  return (
    <aside className="studio-inspector">
      <header className="studio-inspector-header">
        <div className="studio-inspector-heading-row">
          <div>
            <p className="studio-inspector-eyebrow">
              {eyebrow}
            </p>

            <h2>{title}</h2>

            {description && (
              <p>{description}</p>
            )}
          </div>

          {status && (
            <div className="studio-inspector-status">
              {status}
            </div>
          )}
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
