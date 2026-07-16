import type { ReactNode } from "react";

import "./ForgeToolbar.css";

interface ForgeToolbarProps {
  search?: ReactNode;
  actions?: ReactNode;
}

export default function ForgeToolbar({
  search,
  actions,
}: ForgeToolbarProps) {
  return (
    <header className="forge-toolbar">
      <div className="forge-toolbar-search">
        {search}
      </div>

      <div className="forge-toolbar-actions">
        {actions}
      </div>
    </header>
  );
}
