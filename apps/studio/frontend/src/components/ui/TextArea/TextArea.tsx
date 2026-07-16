import type {
  ForwardedRef,
  TextareaHTMLAttributes,
} from "react";
import { forwardRef } from "react";

import "./TextArea.css";

interface TextAreaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean;
}

function TextAreaComponent(
  {
    invalid = false,
    className = "",
    rows = 4,
    ...props
  }: TextAreaProps,
  ref: ForwardedRef<HTMLTextAreaElement>,
) {
  const classes = [
    "numeria-text-area",
    invalid ? "numeria-text-area-invalid" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <textarea
      ref={ref}
      rows={rows}
      className={classes}
      aria-invalid={invalid || undefined}
      {...props}
    />
  );
}

const TextArea = forwardRef(TextAreaComponent);

export default TextArea;
