import Link from "next/link";
import { ArrowLeft, ArrowRight, Save } from "lucide-react";

interface StepNavigationProps {
  patientId: string;
  currentStep: "clinical" | "diagnosis" | "treatment" | "results";
  onSaveAndContinue?: () => void;
  isSaving?: boolean;
}

const STEPS = [
  { id: "clinical", title: "Clinical Input", path: "clinical" },
  { id: "diagnosis", title: "Diagnosis", path: "diagnosis" },
  { id: "treatment", title: "Treatment Plan", path: "treatment" },
  { id: "results", title: "Results", path: "results" },
];

export default function StepNavigation({
  patientId,
  currentStep,
  onSaveAndContinue,
  isSaving = false,
}: StepNavigationProps) {
  const currentIndex = STEPS.findIndex((s) => s.id === currentStep);
  const prevStep = currentIndex > 0 ? STEPS[currentIndex - 1] : null;
  const nextStep =
    currentIndex < STEPS.length - 1 ? STEPS[currentIndex + 1] : null;

  return (
    <div className="mt-8 border-t border-gray-200 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="hidden md:flex items-center gap-2">
        {/* Simple Progress indicators */}
        {STEPS.map((step, idx) => (
          <div key={step.id} className="flex items-center">
            <div
              className={`text-xs font-bold px-2.5 py-1 rounded-full ${idx === currentIndex ? "bg-indigo-600 text-white" : idx < currentIndex ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-400"}`}
            >
              {idx + 1}. {step.title}
            </div>
            {idx < STEPS.length - 1 && (
              <div className="w-4 border-b-2 border-gray-200 mx-1" />
            )}
          </div>
        ))}
      </div>

      <div className="flex w-full sm:w-auto items-center justify-between gap-3">
        {prevStep ? (
          <Link
            href={`/dashboard/patients/${patientId}/${prevStep.path}`}
            className="flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-50 transition"
          >
            <ArrowLeft size={18} />{" "}
            <span className="hidden sm:inline">Previous: {prevStep.title}</span>
            <span className="sm:hidden">Back</span>
          </Link>
        ) : (
          <div></div> // Spacer
        )}

        {nextStep ? (
          onSaveAndContinue ? (
            <button
              onClick={onSaveAndContinue}
              disabled={isSaving}
              className="flex items-center justify-center gap-2 px-5 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-70"
            >
              {isSaving ? (
                "Saving..."
              ) : (
                <>
                  <Save size={18} /> Save & Continue
                </>
              )}
            </button>
          ) : (
            <Link
              href={`/dashboard/patients/${patientId}/${nextStep.path}`}
              className="flex items-center justify-center gap-2 px-5 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              <span className="hidden sm:inline">Next: {nextStep.title}</span>
              <span className="sm:hidden">Next</span> <ArrowRight size={18} />
            </Link>
          )
        ) : (
          <Link
            href={`/dashboard/patients/${patientId}`}
            className="flex items-center justify-center gap-2 px-5 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            <Save size={18} /> Finish Workflow
          </Link>
        )}
      </div>
    </div>
  );
}
