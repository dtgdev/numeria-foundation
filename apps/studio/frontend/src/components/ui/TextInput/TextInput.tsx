import type {
  ForwardedRef,
  InputHTMLAttributes,
} from "react";
import { forwardRef } from "react";

import "./TextInput.css";

interface TextInputProps
  extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
}

function TextInputComponent(
  {
    invalid = false,
    className = "",
    ...props
  }: TextInputProps,
  ref: ForwardedRef<HTMLInputElement>,
) {
  const classes = [
    "numeria-text-input",
    invalid ? "numeria-text-input-invalid" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <input
      ref={ref}
      className={classes}
      aria-invalid={invalid || undefined}
      {...props}
    />
  );
}

const TextInput = forwardRef(TextInputComponent);

export default TextInput;
