import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import "./FormField.css";

interface FormFieldProps {
  label: string;
  htmlFor?: string;
  description?: string;
  error?: string;
  required?: boolean;
  action?: ReactNode;
}

export default function FormField({
  label,
  htmlFor,
  description,
  error,
  required = false,
  action,
  children,
}: PropsWithChildren<FormFieldProps>) {
  return (
    <div
      className={`numeria-form-field ${
        error ? "numeria-form-field-error" : ""
      }`}
    >
      <div className="numeria-form-field-heading">
        <label htmlFor={htmlFor}>
          {label}
          {required && (
            <span aria-hidden="true"> *</span>
          )}
        </label>

        {action && (
          <div className="numeria-form-field-action">
            {action}
          </div>
        )}
      </div>

      {description && (
        <p className="numeria-form-field-description">
          {description}
        </p>
      )}

      {children}

      {error && (
        <p
          className="numeria-form-field-error-message"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
}
