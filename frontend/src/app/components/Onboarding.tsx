import { useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { ArrowRight, Sparkles } from "lucide-react";

export function Onboarding() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    salary: "",
    monthlyExpenses: "",
    currentFD: "",
    currentEPF: "",
    cryptoHoldings: "",
  });
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/dashboard", { state: { userData: formData } });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
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
                type: "number",
                placeholder: "30",
              },
              {
                name: "salary",
                label: "Monthly Salary (₹)",
                type: "number",
                placeholder: "50,000",
              },
              {
                name: "monthlyExpenses",
                label: "Monthly Expenses (₹)",
                type: "number",
                placeholder: "30,000",
              },
              {
                name: "currentFD",
                label: "Current FD Amount (₹)",
                type: "number",
                placeholder: "100,000",
              },
              {
                name: "currentEPF",
                label: "Current EPF Balance (₹)",
                type: "number",
                placeholder: "500,000",
              },
              {
                name: "cryptoHoldings",
                label: "Crypto Holdings (₹)",
                type: "number",
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
                    value={formData[field.name as keyof typeof formData]}
                    onChange={handleChange}
                    onFocus={() => setFocusedField(field.name)}
                    onBlur={() => setFocusedField(null)}
                    placeholder={field.placeholder}
                    required
                    className={`w-full px-4 py-3 bg-[rgba(255,255,255,0.05)] border rounded-xl text-[#E8EDF3] placeholder:text-[#4A5568] transition-all duration-300 ${
                      focusedField === field.name
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
          </div>

          <motion.button
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full mt-8 px-6 py-4 bg-gradient-to-r from-[#00D4FF] to-[#B794F6] rounded-xl text-[#121418] flex items-center justify-center gap-2 shadow-[0_0_30px_rgba(0,212,255,0.5)] transition-all duration-300 hover:shadow-[0_0_40px_rgba(0,212,255,0.7)]"
          >
            <span className="text-lg">Launch Dashboard</span>
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.form>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center mt-6 text-sm text-[#8B92A8]"
        >
          Your data is encrypted and processed locally
        </motion.p>
      </div>
    </motion.div>
  );
}
