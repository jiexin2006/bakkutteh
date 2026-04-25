import { useEffect } from "react";
import { useNavigate } from "react-router";
import { fetchProfiles } from "../lib/api";

export function EntryGate() {
  const navigate = useNavigate();

  useEffect(() => {
    let isActive = true;

    fetchProfiles()
      .then((profilesPayload) => {
        if (!isActive) {
          return;
        }

        if (profilesPayload.profiles.length > 0) {
          navigate("/profiles", { replace: true });
        } else {
          navigate("/onboarding", { replace: true });
        }
      })
      .catch(() => {
        if (!isActive) {
          return;
        }
        navigate("/onboarding", { replace: true });
      });

    return () => {
      isActive = false;
    };
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center text-[#8B92A8]">
      Loading profile...
    </div>
  );
}
