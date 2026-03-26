"use client";

import { useState } from "react";
import { Plus, Trash2, Save } from "lucide-react";
import { Procedure, TreatmentPlan } from "@/lib/types/treatment";
import Button from "@/components/common/Button";
import FormInput from "@/components/common/FormInput";
import Card from "@/components/common/Card";

interface TreatmentPlanFormProps {
  patientId: string;
  initialPlan?: TreatmentPlan;
  onSave: (plan: any) => Promise<void>;
  isLoading?: boolean;
}

export default function TreatmentPlanForm({
  patientId,
  initialPlan,
  onSave,
  isLoading = false,
}: TreatmentPlanFormProps) {
  const [formData, setFormData] = useState({
    title: initialPlan?.title || "",
    dueDateDate: initialPlan?.due_date || "",
    notes: initialPlan?.notes || "",
  });

  const [procedures, setProcedures] = useState<Procedure[]>(
    initialPlan?.procedures || [],
  );

  const [newProcedure, setNewProcedure] = useState<Partial<Procedure>>({});

  const handleAddProcedure = () => {
    if (!newProcedure.name) {
      alert("Please enter procedure name");
      return;
    }

    setProcedures([
      ...procedures,
      {
        ...newProcedure,
        id: `proc_${Date.now()}`,
        status: "PENDING",
      } as Procedure,
    ]);

    setNewProcedure({});
  };

  const handleRemoveProcedure = (id: string | undefined) => {
    if (id) {
      setProcedures(procedures.filter((p) => p.id !== id));
    }
  };

  const handleSave = async () => {
    if (!formData.title) {
      alert("Please enter plan title");
      return;
    }

    if (procedures.length === 0) {
      alert("Please add at least one procedure");
      return;
    }

    const planData = {
      patient_id: patientId,
      title: formData.title,
      procedures,
      due_date: formData.dueDateDate,
      notes: formData.notes,
      total_cost: procedures.reduce((sum, p) => sum + (p.cost || 0), 0),
    };

    await onSave(planData);
  };

  const totalCost = procedures.reduce((sum, p) => sum + (p.cost || 0), 0);

  return (
    <div className="space-y-6">
      {/* Plan Details */}
      <Card>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Treatment Plan Details
        </h3>

        <div className="space-y-4">
          <FormInput
            label="Plan Title"
            value={formData.title}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            placeholder="e.g., Root Canal Treatment"
          />

          <FormInput
            label="Due Date"
            type="date"
            value={formData.dueDateDate}
            onChange={(e) =>
              setFormData({ ...formData, dueDateDate: e.target.value })
            }
          />

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              className="w-full border border-slate-300 rounded-lg p-3 text-sm"
              rows={3}
              placeholder="Treatment plan notes..."
            />
          </div>
        </div>
      </Card>

      {/* Procedures */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Procedures
        </h3>

        {/* Added Procedures */}
        {procedures.length > 0 && (
          <div className="mb-6 space-y-2">
            {procedures.map((proc) => (
              <Card key={proc.id}>
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium text-slate-900">{proc.name}</h4>
                    {proc.description && (
                      <p className="text-sm text-slate-600 mt-1">
                        {proc.description}
                      </p>
                    )}
                    <div className="flex gap-4 mt-2 text-sm text-slate-600">
                      {proc.duration_minutes && (
                        <span>⏱️ {proc.duration_minutes} min</span>
                      )}
                      {proc.cost && <span>💰 Tk {proc.cost}</span>}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveProcedure(proc.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Add Procedure */}
        <Card className="bg-green-50 border-green-200">
          <h4 className="font-medium text-green-900 mb-3">Add Procedure</h4>

          <div className="space-y-3">
            <FormInput
              label="Procedure Name"
              value={newProcedure.name || ""}
              onChange={(e) =>
                setNewProcedure({ ...newProcedure, name: e.target.value })
              }
              placeholder="e.g., Root Canal Treatment"
            />

            <div className="grid grid-cols-2 gap-3">
              <FormInput
                label="Duration (min)"
                type="number"
                value={newProcedure.duration_minutes || ""}
                onChange={(e) =>
                  setNewProcedure({
                    ...newProcedure,
                    duration_minutes: parseInt(e.target.value),
                  })
                }
                placeholder="45"
              />
              <FormInput
                label="Cost (Tk)"
                type="number"
                value={newProcedure.cost || ""}
                onChange={(e) =>
                  setNewProcedure({
                    ...newProcedure,
                    cost: parseFloat(e.target.value),
                  })
                }
                placeholder="5000"
              />
            </div>

            <FormInput
              label="Description"
              value={newProcedure.description || ""}
              onChange={(e) =>
                setNewProcedure({
                  ...newProcedure,
                  description: e.target.value,
                })
              }
              placeholder="Procedure details..."
            />

            <Button
              onClick={handleAddProcedure}
              variant="primary"
              className="w-full"
            >
              <Plus size={18} /> Add Procedure
            </Button>
          </div>
        </Card>
      </div>

      {/* Cost Summary */}
      <Card className="bg-slate-50 border-slate-200">
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold text-slate-900">
            Total Cost:
          </span>
          <span className="text-2xl font-bold text-indigo-600">
            Tk {totalCost.toFixed(2)}
          </span>
        </div>
      </Card>

      {/* Save Button */}
      <Button
        onClick={handleSave}
        variant="primary"
        disabled={isLoading}
        className="w-full"
      >
        <Save size={18} /> Save Treatment Plan
      </Button>
    </div>
  );
}
