import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { motion } from "motion/react";
import { UserRound, PlusCircle, ArrowRight } from "lucide-react";
import { fetchProfiles, selectProfile, fetchSavedUserData, fetchAdvisory, type SavedProfileItem } from "../lib/api";

function formatSavedDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Unknown save date";
  }
  return date.toLocaleString();
}

export function ProfileSelector() {
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<SavedProfileItem[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [switchingId, setSwitchingId] = useState<string | null>(null);

  useEffect(() => {
    fetchProfiles()
      .then((payload) => {
        setProfiles(payload.profiles);
        setActiveProfileId(payload.active_profile_id);
      })
      .catch((fetchError) => {
        setError(fetchError instanceof Error ? fetchError.message : "Failed to load profiles");
      });
  }, []);

  const handleSelectProfile = async (profileId: string) => {
    try {
      setSwitchingId(profileId);
      await selectProfile(profileId);
      // Fetch the new user data after switching profile
      const userData = await fetchSavedUserData();
      
      if (userData) {
        try {
          const toNumber = (value: string): number => {
            const normalized = value.replace(/,/g, "").trim();
            return normalized ? Number(normalized) : 0;
          };
          const advisoryResponse = await fetchAdvisory({
            name: userData.name,
            age: toNumber(userData.age),
            salary: toNumber(userData.salary),
            monthlyExpenses: toNumber(userData.monthlyExpenses),
            currentFD: toNumber(userData.currentFD),
            currentEPF: toNumber(userData.currentEPF),
            cryptoHoldings: toNumber(userData.cryptoHoldings),
            targetRetirementTier: userData.targetRetirementTier,
          });
          localStorage.setItem("bakkutteh_advisory_response", JSON.stringify(advisoryResponse));
          navigate("/dashboard", { state: { userData, advisoryResponse } });
        } catch (e) {
          localStorage.removeItem("bakkutteh_advisory_response");
          navigate("/dashboard", { state: { userData } });
        }
      } else {
        navigate("/dashboard");
      }
    } catch (selectError) {
      setError(selectError instanceof Error ? selectError.message : "Failed to select profile");
    } finally {
      setSwitchingId(null);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen p-6 md:p-10"
    >
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-4xl tracking-tight bg-gradient-to-r from-[#00D4FF] to-[#3EFFA3] bg-clip-text text-transparent">
            Select Saved Profile
          </h1>
          <p className="text-[#8B92A8] mt-2">Choose a profile to continue to dashboard</p>
        </div>

        <div className="space-y-4">
          {error && <p className="text-[#FF8A8A] text-sm">{error}</p>}
          {profiles.length === 0 && !error && (
            <div className="text-center text-[#8B92A8]">No saved profiles found.</div>
          )}

          {profiles.map((profile) => (
            <button
              key={profile.id}
              type="button"
              onClick={() => handleSelectProfile(profile.id)}
              disabled={switchingId !== null}
              className={`w-full text-left backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] hover:border-[#00D4FF66] rounded-2xl p-5 shadow-2xl transition-colors ${switchingId !== null ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-[rgba(0,212,255,0.12)]">
                    <UserRound className="w-5 h-5 text-[#00D4FF]" />
                  </div>
                  <div>
                    <h3 className="text-[#E8EDF3] text-lg">{profile.name}</h3>
                    <p className="text-sm text-[#8B92A8]">Saved: {formatSavedDate(profile.saved_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {activeProfileId === profile.id && switchingId !== profile.id && (
                    <span className="text-xs px-2 py-1 rounded-full bg-[rgba(62,255,163,0.15)] text-[#3EFFA3]">
                      Active
                    </span>
                  )}
                  {switchingId === profile.id && (
                    <span className="text-xs px-2 py-1 rounded-full bg-[rgba(0,212,255,0.15)] text-[#00D4FF]">
                      Loading...
                    </span>
                  )}
                  <ArrowRight className="w-4 h-4 text-[#8B92A8]" />
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-8 flex justify-center">
          <button
            type="button"
            onClick={() => navigate("/onboarding", { state: { createNewProfile: true } })}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-[#B794F6] to-[#FFD700] text-[#121418] flex items-center gap-2"
          >
            <PlusCircle className="w-5 h-5" />
            Create New Profile
          </button>
        </div>
      </div>
    </motion.div>
  );
}
