import { ReactNode } from "react";

interface FormCardProps {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export default function FormCard({
  title,
  description,
  children,
  className = "",
}: FormCardProps) {
  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}
    >
      {title && (
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">{title}</h2>
          {description && (
            <p className="text-gray-700 text-sm mt-1 font-medium">
              {description}
            </p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
