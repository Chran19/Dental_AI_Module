"use client";

interface BadgeProps {
  label: string;
  variant?: "primary" | "success" | "warning" | "danger" | "secondary";
}

const variantClasses = {
  primary: "bg-blue-100 text-blue-800",
  success: "bg-green-100 text-green-800",
  warning: "bg-yellow-100 text-yellow-800",
  danger: "bg-red-100 text-red-800",
  secondary: "bg-slate-100 text-slate-800",
};

export default function Badge({ label, variant = "primary" }: BadgeProps) {
  return (
    <span
      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${variantClasses[variant]}`}
    >
      {label}
    </span>
  );
}
