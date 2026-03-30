interface FormInputProps {
  label?: string;
  error?: string;
  required?: boolean;
  helpText?: string;
  isTextarea?: boolean;
  rows?: number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  value?: string | number;
  type?: string;
  placeholder?: string;
  name?: string;
  id?: string;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  [key: string]: any;
}

export default function FormInput({
  label,
  error,
  required = false,
  helpText,
  isTextarea = false,
  rows = 3,
  ...props
}: FormInputProps) {
  const Component = isTextarea ? "textarea" : "input";

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <Component
        {...props}
        rows={isTextarea ? rows : undefined}
        className={`w-full px-4 py-2.5 border rounded-lg font-medium text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
          error
            ? "border-red-300 bg-red-50 text-red-900"
            : "border-gray-300 bg-white text-gray-900 placeholder-gray-700"
        } disabled:bg-gray-100 disabled:text-gray-700 disabled:cursor-not-allowed`}
      />

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      {helpText && !error && (
        <p className="mt-1 text-xs text-gray-700">{helpText}</p>
      )}
    </div>
  );
}
