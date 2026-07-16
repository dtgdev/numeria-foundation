import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import "./StatusMessage.css";

export type StatusTone =
  | "info"
  | "success"
  | "warning"
  | "danger";

interface StatusMessageProps {
  tone?: StatusTone;
  title?: string;
  action?: ReactNode;
}

export default function StatusMessage({
  children,
  tone = "info",
  title,
  action,
}: PropsWithChildren<StatusMessageProps>) {
  return (
    <div
      className={`numeria-status-message numeria-status-${tone}`}
      role={tone === "danger" ? "alert" : "status"}
    >
      <div>
        {title && <strong>{title}</strong>}

        <div className="numeria-status-content">
          {children}
        </div>
      </div>

      {action && (
        <div className="numeria-status-action">
          {action}
        </div>
      )}
    </div>
  );
}
