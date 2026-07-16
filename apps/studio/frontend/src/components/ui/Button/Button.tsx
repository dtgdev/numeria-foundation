import type {
  ButtonHTMLAttributes,
  PropsWithChildren,
} from "react";

import "./Button.css";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "danger"
  | "ghost";

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
}

export default function Button({
  children,
  variant = "primary",
  fullWidth = false,
  className = "",
  type = "button",
  ...props
}: PropsWithChildren<ButtonProps>) {
  const classes = [
    "numeria-button",
    `numeria-button-${variant}`,
    fullWidth ? "numeria-button-full-width" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type={type}
      className={classes}
      {...props}
    >
      {children}
    </button>
  );
}
