import {
  useEffect,
  type PropsWithChildren,
  type ReactNode,
} from "react";

import Button from "../Button/Button";
import "./Dialog.css";

interface DialogProps {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  footer?: ReactNode;
  width?: "small" | "medium" | "large";
}

export default function Dialog({
  open,
  title,
  description,
  onClose,
  footer,
  width = "medium",
  children,
}: PropsWithChildren<DialogProps>) {
  useEffect(() => {
    if (!open) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="numeria-dialog-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <section
        className={`numeria-dialog numeria-dialog-${width}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="numeria-dialog-title"
      >
        <header className="numeria-dialog-header">
          <div>
            <h2 id="numeria-dialog-title">{title}</h2>

            {description && <p>{description}</p>}
          </div>

          <Button
            variant="ghost"
            className="numeria-dialog-close"
            onClick={onClose}
            aria-label="Close dialog"
          >
            ×
          </Button>
        </header>

        <div className="numeria-dialog-body">
          {children}
        </div>

        {footer && (
          <footer className="numeria-dialog-footer">
            {footer}
          </footer>
        )}
      </section>
    </div>
  );
}
