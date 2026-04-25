import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowRight, Sparkles } from "lucide-react";
import { createProfile, fetchAdvisory, fetchSavedUserData, resetSavedUserData, saveUserData } from "../lib/api";
import type { AdvisoryResponse, UserData } from "../lib/api";

const ADVISORY_STORAGE_KEY = "bakkutteh_advisory_response";

const NUMERIC_FIELDS = new Set([
  "age",
  "salary",
  "monthlyExpenses",
  "currentFD",
  "currentEPF",
  "cryptoHoldings",
]);

export function Onboarding() {
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState<UserData>({
    name: "",
    age: "",
    salary: "",
    monthlyExpenses: "",
    currentFD: "",
    currentEPF: "",
    cryptoHoldings: "",
    targetRetirementTier: "basic",
  });
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitStage, setSubmitStage] = useState<string>("");
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);
  const createNewProfile = Boolean(location.state?.createNewProfile);

  useEffect(() => {
    if (createNewProfile) {
      return;
    }

    fetchSavedUserData()
      .then((savedProfile) => {
        if (savedProfile) {
          setFormData(savedProfile);
        }
      })
      .catch(() => {
        // Silently ignore profile load issues and keep defaults.
      });
  }, []);

  useEffect(() => {
    if (!isSubmitting) {
      setElapsedSeconds(0);
      return;
    }

    const timer = window.setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isSubmitting]);

  const toNumber = (value: string): number => {
    const normalized = value.replace(/,/g, "").trim();
    return normalized ? Number(normalized) : 0;
  };

  // remove when Z.ai is stable and fallback is no longer needed

  const buildLocalFallbackResponse = (errorMessage: string): AdvisoryResponse => {
    const age = toNumber(formData.age);
    const salary = toNumber(formData.salary);
    const monthlyExpenses = toNumber(formData.monthlyExpenses);
    const currentEPF = toNumber(formData.currentEPF);
    const surplus = Math.max(0, salary - monthlyExpenses);

    return {
      request_id: `local-fallback-${Date.now()}`,
      advisory_source: "fallback",
      advisory_label: "TEMPORARY_FALLBACK",
      advisory_error: errorMessage,
      user_profile: {
        user_id: formData.name,
        age,
        current_epf_balance_rm: currentEPF,
        current_surplus_rm: surplus,
      },
      epf_analysis: {
        status: "Fallback",
        deficit_percentage: 0,
        priority_level: "Medium",
        selected_target_rm: 0,
        deficit_rm: 0,
      },
      market_signals: {
        bitcoin_signal: "HOLD",
        bitcoin_confidence: 0.3,
        bitcoin_trend: "Neutral",
      },
      advisory_json: {
        overall_strategy: "Temporary fallback allocation while live advisory is unavailable",
        safety_gauge: "Medium",
        action_plan: [
          {
            percentage: "40%",
            category: "EPF",
            action: "Top-up EPF via i-Akaun",
            reasoning: "Fallback prioritizes retirement safety until live AI response recovers.",
          },
          {
            percentage: "40%",
            category: "FD",
            action: "Place funds in a verified 12-month FD option",
            reasoning: "Fallback emphasizes stable returns while model endpoint is unavailable.",
          },
          {
            percentage: "20%",
            category: "Crypto",
            action: "Hold small BTC allocation",
            reasoning: "Risk is capped during fallback mode.",
          },
        ],
        next_step: "You are viewing temporary fallback advice. Retry shortly for live AI output.",
      },
    };
  };
  // until here

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);
    setSubmitStage("Sending profile to backend...");

    try {
      setSubmitStage("Backend is preparing EPF and market context...");
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

      setSubmitStage("Advisory received. Rendering dashboard...");

      navigate("/dashboard", {
        state: {
          userData: formData,
          advisoryResponse,
        },
      });
      try {
        if (createNewProfile) {
          await createProfile(formData);
        } else {
          await saveUserData(formData);
        }
      } catch {
        // Keep advisory flow available even if profile persistence is unavailable.
      }
      localStorage.setItem(ADVISORY_STORAGE_KEY, JSON.stringify(advisoryResponse));
    } catch (error) {

      const errorMessage = error instanceof Error ? error.message : "Unable to generate advisory right now.";
      setSubmitStage("Live advisory failed. Loading temporary fallback...");

      const advisoryResponse = buildLocalFallbackResponse(errorMessage);
      try {
        if (createNewProfile) {
          await createProfile(formData);
        } else {
          await saveUserData(formData);
        }
      } catch {
        // Keep fallback flow available even if profile persistence is unavailable.
      }
      localStorage.setItem(ADVISORY_STORAGE_KEY, JSON.stringify(advisoryResponse));
      navigate("/dashboard", {
        state: {
          userData: formData,
          advisoryResponse,
        },
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const sanitizedValue = NUMERIC_FIELDS.has(name)
      ? value.replace(/[^0-9,]/g, "")
      : value;

    const nextFormData = { ...formData, [name]: sanitizedValue };
    setFormData(nextFormData);
  };

  const handleResetSavedProfile = async () => {
    try {
      await resetSavedUserData();
      setFormData({
        name: "",
        age: "",
        salary: "",
        monthlyExpenses: "",
        currentFD: "",
        currentEPF: "",
        cryptoHoldings: "",
        targetRetirementTier: "basic",
      });
      setSubmitError(null);
      localStorage.removeItem(ADVISORY_STORAGE_KEY);
    } catch {
      setSubmitError("Unable to reset saved profile right now. Please try again.");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      className="min-h-screen flex items-center justify-center p-6"
    >
      <div className="w-full max-w-xl">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-[#00D4FF]" />
            <h1 className="text-5xl tracking-tight bg-gradient-to-r from-[#00D4FF] via-[#B794F6] to-[#FFD700] bg-clip-text text-transparent">
              Initialize Financial Profile
            </h1>
          </div>
          <p className="text-lg text-[#8B92A8]">
            Let's configure your intelligent advisory system
          </p>
        </motion.div>

        <motion.form
          onSubmit={handleSubmit}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-8 shadow-2xl"
        >
          <div className="space-y-6">
            {[
              { name: "name", label: "Full Name", type: "text", placeholder: "John Doe" },
              {
                name: "age",
                label: "Age",
                type: "text",
                placeholder: "30",
              },
              {
                name: "salary",
                label: "Monthly Salary (RM)",
                type: "text",
                placeholder: "50,000",
              },
              {
                name: "monthlyExpenses",
                label: "Monthly Expenses (RM)",
                type: "text",
                placeholder: "30,000",
              },
              {
                name: "currentFD",
                label: "Current FD Amount (RM)",
                type: "text",
                placeholder: "100,000",
              },
              {
                name: "currentEPF",
                label: "Current EPF Balance (RM)",
                type: "text",
                placeholder: "500,000",
              },
              {
                name: "cryptoHoldings",
                label: "Crypto Holdings (RM)",
                type: "text",
                placeholder: "25,000",
              },
            ].map((field, index) => (
              <motion.div
                key={field.name}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.5 + index * 0.1 }}
              >
                <label htmlFor={field.name} className="block mb-2 text-[#E8EDF3]">
                  {field.label}
                </label>
                <div className="relative">
                  <input
                    id={field.name}
                    name={field.name}
                    type={field.type}
                    inputMode={NUMERIC_FIELDS.has(field.name) ? "numeric" : undefined}
                    value={formData[field.name as keyof typeof formData]}
                    onChange={handleChange}
                    onFocus={() => setFocusedField(field.name)}
                    onBlur={() => setFocusedField(null)}
                    placeholder={field.placeholder}
                    required
                    className={`w-full px-4 py-3 bg-[rgba(255,255,255,0.05)] border rounded-xl text-[#E8EDF3] placeholder:text-[#4A5568] transition-all duration-300 ${focusedField === field.name
                        ? "border-[#00D4FF] shadow-[0_0_20px_rgba(0,212,255,0.3)]"
                        : "border-[rgba(255,255,255,0.1)]"
                      }`}
                  />
                  {focusedField === field.name && (
                    <motion.div
                      layoutId="glow"
                      className="absolute -inset-0.5 bg-gradient-to-r from-[#00D4FF] to-[#B794F6] rounded-xl opacity-20 -z-10 blur-sm"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 0.2 }}
                    />
                  )}
                </div>
              </motion.div>
            ))}

            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 + 7 * 0.1 }}
            >
              <label htmlFor="targetRetirementTier" className="block mb-2 text-[#E8EDF3]">
                EPF Saving Level
              </label>
              <div className="relative">
                <select
                  id="targetRetirementTier"
                  name="targetRetirementTier"
                  value={formData.targetRetirementTier}
                  onChange={(e) => setFormData({ ...formData, targetRetirementTier: e.target.value })}
                  className="w-full px-4 py-3 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl text-[#E8EDF3] appearance-none focus:border-[#00D4FF] focus:shadow-[0_0_20px_rgba(0,212,255,0.3)] outline-none transition-all duration-300"
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
            </motion.div>
          </div>

          <motion.button
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            disabled={isSubmitting}
            className="w-full mt-8 px-6 py-4 bg-gradient-to-r from-[#00D4FF] to-[#B794F6] rounded-xl text-[#121418] flex items-center justify-center gap-2 shadow-[0_0_30px_rgba(0,212,255,0.5)] transition-all duration-300 hover:shadow-[0_0_40px_rgba(0,212,255,0.7)]"
          >
            <span className="text-lg">{isSubmitting ? "Generating Advisory..." : "Launch Dashboard"}</span>
            <ArrowRight className="w-5 h-5" />
          </motion.button>
          {isSubmitting && (
            <p className="mt-3 text-sm text-[#8B92A8]">
              {submitStage} ({elapsedSeconds}s)
            </p>
          )}
          {submitError && (
            <p className="mt-4 text-sm text-[#FF8A8A]">{submitError}</p>
          )}
        </motion.form>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center mt-6 text-sm text-[#8B92A8]"
        >
          Your data is encrypted and processed locally
        </motion.p>
        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={handleResetSavedProfile}
            className="px-4 py-2 rounded-lg border border-[rgba(255,255,255,0.2)] text-sm text-[#E8EDF3] hover:border-[#00D4FF] hover:text-[#00D4FF] transition-colors"
          >
            Reset Saved Profile
          </button>
        </div>
      </div>
    </motion.div>
  );
}
