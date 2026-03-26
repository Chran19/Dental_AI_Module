"use client";

import { useState } from "react";
import { Plus, Trash2, Download } from "lucide-react";
import { Card as CardType } from "@/lib/types/prescription";
import Button from "@/components/common/Button";
import FormInput from "@/components/common/FormInput";

interface PrescriptionBuilderProps {
  initialMedicines?: CardType[];
  onSave: (medicines: CardType[], notes: string) => void;
  isLoading?: boolean;
}

export default function PrescriptionBuilder({
  initialMedicines = [],
  onSave,
  isLoading = false,
}: PrescriptionBuilderProps) {
  const [medicines, setMedicines] = useState<CardType[]>(initialMedicines);
  const [notes, setNotes] = useState("");
  const [newMedicine, setNewMedicine] = useState<Partial<CardType>>({});

  const handleAddMedicine = () => {
    if (!newMedicine.name || !newMedicine.dosage || !newMedicine.frequency) {
      alert("Please fill in name, dosage, and frequency");
      return;
    }

    setMedicines([
      ...medicines,
      {
        ...newMedicine,
        id: `med_${Date.now()}`,
      } as CardType,
    ]);
    setNewMedicine({});
  };

  const handleRemove = (id: string | undefined) => {
    if (id) {
      setMedicines(medicines.filter((m) => m.id !== id));
    }
  };

  const handleSave = () => {
    if (medicines.length === 0) {
      alert("Please add at least one medicine");
      return;
    }
    onSave(medicines, notes);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Prescription Builder
        </h3>

        {/* Existing Medicines */}
        {medicines.length > 0 && (
          <div className="mb-6">
            <h4 className="font-medium text-slate-700 mb-3">Added Medicines</h4>
            <div className="space-y-2">
              {medicines.map((med) => (
                <div
                  key={med.id}
                  className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200"
                >
                  <div>
                    <p className="font-medium text-slate-900">{med.name}</p>
                    <p className="text-sm text-slate-600">
                      {med.dosage} • {med.frequency}
                      {med.duration_days ? ` • ${med.duration_days} days` : ""}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemove(med.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Add New Medicine */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4 space-y-3">
          <h4 className="font-medium text-blue-900">Add New Medicine</h4>

          <div className="grid grid-cols-2 gap-3">
            <FormInput
              label="Medicine Name"
              value={newMedicine.name || ""}
              onChange={(e) =>
                setNewMedicine({ ...newMedicine, name: e.target.value })
              }
              placeholder="e.g., Amoxicillin"
            />
            <FormInput
              label="Dosage"
              value={newMedicine.dosage || ""}
              onChange={(e) =>
                setNewMedicine({ ...newMedicine, dosage: e.target.value })
              }
              placeholder="e.g., 500mg"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <FormInput
              label="Frequency"
              value={newMedicine.frequency || ""}
              onChange={(e) =>
                setNewMedicine({ ...newMedicine, frequency: e.target.value })
              }
              placeholder="e.g., 3 times daily"
            />
            <FormInput
              label="Duration (days)"
              type="number"
              value={newMedicine.duration_days || ""}
              onChange={(e) =>
                setNewMedicine({
                  ...newMedicine,
                  duration_days: parseInt(e.target.value),
                })
              }
              placeholder="e.g., 7"
            />
          </div>

          <Button
            onClick={handleAddMedicine}
            variant="primary"
            className="w-full"
          >
            <Plus size={18} /> Add Medicine
          </Button>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Additional Notes
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full border border-slate-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          rows={4}
          placeholder="Any special instructions or notes for the patient..."
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          onClick={handleSave}
          variant="primary"
          disabled={isLoading}
          className="flex-1"
        >
          <Download size={18} /> Save Prescription
        </Button>
      </div>
    </div>
  );
}
