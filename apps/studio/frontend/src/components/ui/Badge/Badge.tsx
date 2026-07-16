import type {
  HTMLAttributes,
  PropsWithChildren,
} from "react";

import "./Badge.css";

export type BadgeTone =
  | "neutral"
  | "brand"
  | "success"
  | "warning"
  | "danger";

interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

export default function Badge({
  children,
  tone = "neutral",
  className = "",
  ...props
}: PropsWithChildren<BadgeProps>) {
  const classes = [
    "numeria-badge",
    `numeria-badge-${tone}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={classes} {...props}>
      {children}
    </span>
  );
}
