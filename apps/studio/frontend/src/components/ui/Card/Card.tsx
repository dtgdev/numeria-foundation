import type {
  HTMLAttributes,
  PropsWithChildren,
  ReactNode,
} from "react";

import "./Card.css";

interface CardProps extends HTMLAttributes<HTMLElement> {
  title?: string;
  description?: string;
  action?: ReactNode;
  padding?: "none" | "small" | "medium" | "large";
}

export default function Card({
  children,
  title,
  description,
  action,
  padding = "medium",
  className = "",
  ...props
}: PropsWithChildren<CardProps>) {
  const classes = [
    "numeria-card",
    `numeria-card-padding-${padding}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <section className={classes} {...props}>
      {(title || description || action) && (
        <header className="numeria-card-header">
          <div>
            {title && <h2>{title}</h2>}
            {description && <p>{description}</p>}
          </div>

          {action && (
            <div className="numeria-card-action">
              {action}
            </div>
          )}
        </header>
      )}

      {children}
    </section>
  );
}
