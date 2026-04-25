import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowLeft, Save } from "lucide-react";
import { fetchProfiles, fetchSavedUserData, updateProfile, fetchAdvisory, type UserData } from "../lib/api";

const NUMERIC_FIELDS = new Set([
  "age",
  "salary",
  "monthlyExpenses",
  "currentFD",
  "currentEPF",
  "cryptoHoldings",
]);

const EMPTY_FORM: UserData = {
  name: "",
  age: "",
  salary: "",
  monthlyExpenses: "",
  currentFD: "",
  currentEPF: "",
  cryptoHoldings: "",
  targetRetirementTier: "basic",
};

export function ProfileSettings() {
  const navigate = useNavigate();
  const [profileId, setProfileId] = useState<string | null>(null);
  const [formData, setFormData] = useState<UserData>(EMPTY_FORM);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    Promise.all([fetchProfiles(), fetchSavedUserData()])
      .then(([profilesPayload, userData]) => {
        setProfileId(profilesPayload.active_profile_id);
        if (userData) {
          setFormData(userData);
        }
      })
      .catch((fetchError) => {
        setError(fetchError instanceof Error ? fetchError.message : "Failed to load profile settings");
      });
  }, []);

  const fields = useMemo(
    () => [
      { name: "name", label: "Full Name", placeholder: "John Doe" },
      { name: "age", label: "Age", placeholder: "30" },
      { name: "salary", label: "Monthly Salary (RM)", placeholder: "50,000" },
      { name: "monthlyExpenses", label: "Monthly Expenses (RM)", placeholder: "30,000" },
      { name: "currentFD", label: "Current FD Amount (RM)", placeholder: "100,000" },
      { name: "currentEPF", label: "Current EPF Balance (RM)", placeholder: "500,000" },
      { name: "cryptoHoldings", label: "Crypto Holdings (RM)", placeholder: "25,000" },
    ],
    [],
  );

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    const sanitized = NUMERIC_FIELDS.has(name) ? value.replace(/[^0-9,]/g, "") : value;
    setFormData((previous) => ({ ...previous, [name]: sanitized }));
  };

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage(null);
    setError(null);
    setIsSaving(true);

    if (!profileId) {
      setError("No active profile selected. Please choose a profile first.");
      setIsSaving(false);
      return;
    }

    try {
      await updateProfile(profileId, formData);

      try {
        const toNumber = (value: string): number => {
          const normalized = value.replace(/,/g, "").trim();
          return normalized ? Number(normalized) : 0;
        };
        const advisoryResponse = await fetchAdvisory({
          name: formData.name,
          age: toNumber(formData.age),
          salary: toNumber(formData.salary),
          monthlyExpenses: toNumber(formData.monthlyExpenses),
          currentFD: toNumber(formData.currentFD),
          currentEPF: toNumber(formData.currentEPF),
          cryptoHoldings: toNumber(formData.cryptoHoldings),
          targetRetirementTier: formData.targetRetirementTier,
        });
        localStorage.setItem("bakkutteh_advisory_response", JSON.stringify(advisoryResponse));
      } catch (e) {
        localStorage.removeItem("bakkutteh_advisory_response");
      }

      setMessage("Profile updated successfully.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save profile");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      className="min-h-screen p-6 md:p-10"
    >
      <div className="max-w-2xl mx-auto">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          className="mb-6 flex items-center gap-2 text-[#8B92A8] hover:text-[#00D4FF]"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </button>

        <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-8 shadow-2xl">
          <h1 className="text-3xl bg-gradient-to-r from-[#00D4FF] to-[#B794F6] bg-clip-text text-transparent">
            Profile Settings
          </h1>
          <p className="text-[#8B92A8] mt-2">Review and update your current profile information.</p>

          <form className="mt-8 space-y-5" onSubmit={handleSave}>
            {fields.map((field) => (
              <div key={field.name}>
                <label htmlFor={field.name} className="block mb-2 text-[#E8EDF3]">
                  {field.label}
                </label>
                <input
                  id={field.name}
                  name={field.name}
                  value={formData[field.name as keyof UserData]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl text-[#E8EDF3]"
                />
              </div>
            ))}

            <div>
              <label htmlFor="targetRetirementTier" className="block mb-2 text-[#E8EDF3]">
                EPF Saving Level
              </label>
              <div className="relative">
                <select
                  id="targetRetirementTier"
                  name="targetRetirementTier"
                  value={formData.targetRetirementTier}
                  onChange={(e) => setFormData({ ...formData, targetRetirementTier: e.target.value })}
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl text-[#E8EDF3] appearance-none focus:border-[#00D4FF] outline-none transition-all duration-300"
                >
                  <option value="basic" className="bg-[#1E222A]">Basic</option>
                  <option value="adequate" className="bg-[#1E222A]">Adequate</option>
                  <option value="enhanced" className="bg-[#1E222A]">Enhanced</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-[#8B92A8]">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                  </svg>
                </div>
              </div>
            </div>

            {message && <p className="text-sm text-[#3EFFA3]">{message}</p>}
            {error && <p className="text-sm text-[#FF8A8A]">{error}</p>}

            <button
              type="submit"
              disabled={isSaving}
              className={`mt-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#00D4FF] to-[#B794F6] text-[#121418] flex items-center gap-2 ${isSaving ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              <Save className="w-4 h-4" />
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
}
