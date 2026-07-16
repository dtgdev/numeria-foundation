import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import StudioInspector from
  "../StudioInspector/StudioInspector";

import StudioNavigation from
  "../StudioNavigation/StudioNavigation";

import type {
  StudioSection,
} from "../StudioNavigation/StudioNavigation";

import "./StudioShell.css";

interface StudioShellProps {
  activeSection: StudioSection;
  onSectionChange: (section: StudioSection) => void;
  inspectorTitle: string;
  inspectorDescription?: string;
  inspectorContent?: ReactNode;
  inspectorActions?: ReactNode;
  toolbar?: ReactNode;
}

export default function StudioShell({
  activeSection,
  onSectionChange,
  inspectorTitle,
  inspectorDescription,
  inspectorContent,
  inspectorActions,
  toolbar,
  children,
}: PropsWithChildren<StudioShellProps>) {
  return (
    <div className="genesis-shell">
      <StudioNavigation
        activeSection={activeSection}
        onSelect={onSectionChange}
      />

      <section className="genesis-workspace">
        <header className="genesis-toolbar">
          <div>
            <p>NUMERIA STUDIO</p>
            <h1>
              {activeSection === "world"
                ? "World Studio"
                : activeSection === "characters"
                  ? "Character Studio"
                  : activeSection === "relationships"
                    ? "Relationship Studio"
                    : "Canon Explorer"}
            </h1>
          </div>

          {toolbar && (
            <div className="genesis-toolbar-actions">
              {toolbar}
            </div>
          )}
        </header>

        <main className="genesis-canvas">
          {children}
        </main>
      </section>

      <StudioInspector
        title={inspectorTitle}
        description={inspectorDescription}
        actions={inspectorActions}
      >
        {inspectorContent}
      </StudioInspector>
    </div>
  );
}
