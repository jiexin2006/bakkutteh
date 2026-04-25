import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Shield,
  Zap,
  ArrowRight,
  Activity,
  DollarSign,
} from "lucide-react";
import {
  LineChart,
  Line,
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import {
  fetchSavedUserData,
  fetchBitcoinAdvisory,
  fetchFDRankings,
  type AdvisoryResponse,
  type BitcoinAdvisoryResponse,
  type FDRanking,
  type UserData,
} from "../lib/api";

type DashboardFDRanking = FDRanking & {
  display_bank: string;
  display_tenure: string;
  progress: number;
};

const ADVISORY_STORAGE_KEY = "bakkutteh_advisory_response";

function readStorage<T>(key: string): T | undefined {
  try {
    const value = localStorage.getItem(key);
    return value ? (JSON.parse(value) as T) : undefined;
  } catch {
    return undefined;
  }
}

function formatCurrency(value: number | string | undefined, fallback: string): string {
  if (value === undefined || value === null) {
    return fallback;
  }

  if (typeof value === "number") {
    return value.toLocaleString();
  }

  const numeric = Number(value.toString().replace(/,/g, ""));
  if (Number.isNaN(numeric)) {
    return fallback;
  }
  return numeric.toLocaleString();
}

// Add this helper function - EPF Health Color Helper
function getEPFHealthColor(epfHealth: number): { 
  fill: string; 
  glowColor: string; 
  textColor: string 
} {
  if (epfHealth >= 75) {
    return {
      fill: "#3EFFA3", // Green - On Track
      glowColor: "rgba(62, 255, 163, 0.5)",
      textColor: "#3EFFA3",
    };
  } else if (epfHealth >= 50) {
    return {
      fill: "#FFD166", // Yellow - Medium
      glowColor: "rgba(255, 209, 102, 0.5)",
      textColor: "#FFD166",
    };
  } else if (epfHealth >= 25) {
    return {
      fill: "#FF9A5A", // Orange - High
      glowColor: "rgba(255, 154, 90, 0.5)",
      textColor: "#FF9A5A",
    };
  } else {
    return {
      fill: "#FF5A6B", // Red - Critical
      glowColor: "rgba(255, 90, 107, 0.5)",
      textColor: "#FF5A6B",
    };
  }
}

export function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | undefined>(location.state?.userData);
  const advisoryResponse =
    (location.state?.advisoryResponse as AdvisoryResponse | undefined) ??
    readStorage<AdvisoryResponse>(ADVISORY_STORAGE_KEY);
  const [fdRankings, setFdRankings] = useState<DashboardFDRanking[]>([]);
  const [fdRankingsError, setFdRankingsError] = useState<string | null>(null);
  const [bitcoinAdvisory, setBitcoinAdvisory] = useState<BitcoinAdvisoryResponse | null>(null);
  const [bitcoinAdvisoryError, setBitcoinAdvisoryError] = useState<string | null>(null);

  useEffect(() => {
    if (userData) {
      return;
    }

    fetchSavedUserData()
      .then((savedProfile) => {
        if (savedProfile) {
          setUserData(savedProfile);
        }
      })
      .catch(() => {
        // Keep empty fallback when saved profile is unavailable.
      });
  }, [userData]);

  useEffect(() => {
    let isActive = true;

    fetchFDRankings(6)
      .then((response) => {
        if (!isActive) return;

        const maxRate = Math.max(
          ...response.verified_market_rates.map((item) => item.interest_rate_pct || 0),
          1,
        );

        const normalized = response.verified_market_rates
          .filter((item) => item.bank_name && item.interest_rate_pct !== null)
          .map((item) => ({
            ...item,
            display_bank: `${item.bank_name}${item.account_type ? ` ${item.account_type}` : ""}`,
            display_tenure: `${item.tenure_months || 0} months`,
            progress: Math.max(10, Math.round(((item.interest_rate_pct || 0) / maxRate) * 100)),
          }))
          .sort((left, right) => (right.interest_rate_pct || 0) - (left.interest_rate_pct || 0));

        setFdRankings(normalized);
      })
      .catch((error) => {
        if (!isActive) return;
        setFdRankingsError(error instanceof Error ? error.message : "Failed to load FD rankings");
      });

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    let isActive = true;

    fetchBitcoinAdvisory()
      .then((response) => {
        if (!isActive) return;
        setBitcoinAdvisory(response);
      })
      .catch((error) => {
        if (!isActive) return;
        setBitcoinAdvisoryError(error instanceof Error ? error.message : "Failed to load Bitcoin advisory");
      });

    return () => {
      isActive = false;
    };
  }, []);

  // Calculate EPF Health based on deficit percentage
  const epfHealth = Math.max(
    0,
    Math.min(
      100,
      100 - Number(advisoryResponse?.epf_analysis?.deficit_percentage ?? 15),
    ),
  );

  // Get color based on health
  const { fill, glowColor, textColor } = getEPFHealthColor(epfHealth);
  
  // Create data with dynamic fill
  const epfData = [{ name: "EPF Health", value: epfHealth, fill: fill }];
  
  const growthPriority = advisoryResponse?.epf_analysis?.priority_level || "No Priority";
  const growthColorClass =
    growthPriority === "Critical"
      ? "text-[#FF5A6B]"
      : growthPriority === "High"
      ? "text-[#FF9A5A]"
      : growthPriority === "Medium"
      ? "text-[#FFD166]"
      : "text-[#3EFFA3]";

  const currentBtcPriceLabel =
    typeof bitcoinAdvisory?.current_price_myr === "number"
      ? `RM${Math.round(bitcoinAdvisory.current_price_myr).toLocaleString()}`
      : "--";

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      className="min-h-screen p-6 md:p-10"
    >
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8 flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl md:text-5xl tracking-tight bg-gradient-to-r from-[#00D4FF] to-[#3EFFA3] bg-clip-text text-transparent">
              Financial Command Center
            </h1>
            <p className="text-[#8B92A8] mt-2">
              Welcome back, {userData?.name || "User"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/profile")}
              className="px-5 py-3 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.15)] rounded-xl text-[#E8EDF3] hover:border-[#00D4FF] hover:text-[#00D4FF] transition-colors"
            >
              Profile Info
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/profiles")}
              className="px-5 py-3 bg-[rgba(255,255,255,0.06)] border border-[rgba(255,255,255,0.15)] rounded-xl text-[#E8EDF3] hover:border-[#3EFFA3] hover:text-[#3EFFA3] transition-colors"
            >
              Switch Profile
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() =>
                navigate("/advisory", {
                  state: {
                    userData,
                    advisoryResponse,
                  },
                })
              }
              className="px-6 py-3 bg-gradient-to-r from-[#B794F6] to-[#FFD700] rounded-xl text-[#121418] flex items-center gap-2 shadow-[0_0_25px_rgba(183,148,246,0.5)]"
            >
              <Zap className="w-5 h-5" />
              <span>AI Advisory</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-7"
          >
            <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl h-full flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-[rgba(0,212,255,0.1)] rounded-lg">
                  <DollarSign className="w-6 h-6 text-[#00D4FF]" />
                </div>
                <h2 className="text-2xl text-[#E8EDF3]">FD Rankings</h2>
              </div>
              {fdRankingsError && (
                <p className="mb-4 text-sm text-[#FF8A8A]">{fdRankingsError}</p>
              )}
              <div className="space-y-4 h-[22rem] overflow-y-auto pr-2">
                {fdRankings.length === 0 && !fdRankingsError && (
                  <p className="text-sm text-[#8B92A8]">Loading verified FD rankings from backend...</p>
                )}
                {fdRankings.map((fd, index) => (
                  <motion.div
                    key={`${fd.bank_name}-${fd.tenure_months}-${index}`}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="group hover:bg-[rgba(0,212,255,0.05)] p-4 rounded-xl transition-all duration-300 border border-transparent hover:border-[rgba(0,212,255,0.3)]"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-[#E8EDF3]">{fd.display_bank}</h3>
                        <p className="text-sm text-[#8B92A8]">
                          Min placement: RM{(fd.min_placement_rm || 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-[#8B92A8] mt-1">{fd.display_tenure}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl text-[#00D4FF]">{fd.interest_rate_pct?.toFixed(2)}%</div>
                        <p className="text-xs text-[#8B92A8]">p.a.</p>
                      </div>
                    </div>
                    <div className="relative h-2 bg-[rgba(255,255,255,0.05)] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${fd.progress}%` }}
                        transition={{ delay: 0.6 + index * 0.1, duration: 0.8 }}
                        className="absolute h-full bg-gradient-to-r from-[#00D4FF] to-[#00A3CC] rounded-full"
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-5"
          >
            <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl h-full">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg" style={{ backgroundColor: glowColor }}>
                  <Shield className="w-6 h-6" style={{ color: textColor }} />
                </div>
                <h2 className="text-2xl text-[#E8EDF3]">EPF Health</h2>
              </div>
              <div className="flex items-center justify-center h-64 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="60%"
                    outerRadius="90%"
                    barSize={20}
                    data={epfData}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <defs>
                      <filter id="glow" x="-20%" y="-20%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                      </filter>
                    </defs>

                    <RadialBar
                      background
                      dataKey="value"
                      cornerRadius={10}
                      fill={fill}
                      style={{ filter: "url(#glow)" }}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>

                {/* Centered Text */}
                <div className="absolute text-center">
                  <div className="text-4xl font-bold" style={{ color: textColor }}>
                    {Math.round(epfHealth)}%
                  </div>
                  <p className="text-sm text-[#8B92A8] mt-1">
                    {advisoryResponse?.epf_analysis?.status || "Optimal"}
                    {advisoryResponse?.epf_analysis?.target_epf_level && (
                      <span className="block text-[10px] uppercase tracking-wider opacity-60">
                        Level: {advisoryResponse.epf_analysis.target_epf_level}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div 
                  className="p-3 rounded-lg border"
                  style={{ 
                    backgroundColor: `${glowColor}30`, 
                    borderColor: `${textColor}50` 
                  }}
                >
                  <p className="text-xs text-[#8B92A8]">Balance</p>
                  <p className="text-xl mt-1" style={{ color: textColor }}>
                    RM{formatCurrency(userData?.currentEPF, "500,000")}
                  </p>
                </div>
                <div 
                  className="p-3 rounded-lg border"
                  style={{ 
                    backgroundColor: `${glowColor}30`, 
                    borderColor: `${textColor}50` 
                  }}
                >
                  <p className="text-xs text-[#8B92A8]">Growth</p>
                  <p className="text-xl mt-1" style={{ color: textColor }}>
                    {growthPriority}
                  </p>
                </div>
              </div>
              <p className="mt-4 text-center text-sm" style={{ color: textColor }}>
                EPF Health Score: {Math.round(epfHealth)}%
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-12"
          >
            <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[rgba(183,148,246,0.1)] rounded-lg">
                    <Activity className="w-6 h-6 text-[#B794F6]" />
                  </div>
                  <div>
                    <h2 className="text-2xl text-[#E8EDF3]">Crypto Intelligence</h2>
                    <p className="text-sm text-[#8B92A8]">BTC/MYR - Latest market snapshot</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl bg-gradient-to-r from-[#B794F6] to-[#FFD700] bg-clip-text text-transparent">
                    {currentBtcPriceLabel}
                  </div>
                  <div className="flex items-center gap-1 text-[#3EFFA3] text-sm mt-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>
                      {bitcoinAdvisory ? `${bitcoinAdvisory.forecast_change_pct >= 0 ? "+" : ""}${bitcoinAdvisory.forecast_change_pct.toFixed(2)}%` : "Loading..."}
                    </span>
                  </div>
                  <div className={`text-xs mt-2 ${bitcoinAdvisory?.price_source === "predicted" ? "text-[#FFD166]" : "text-[#3EFFA3]"}`}>
                    {bitcoinAdvisory?.price_status || "Loading..."}
                  </div>
                </div>
              </div>
              {bitcoinAdvisoryError ? (
                <p className="text-sm text-[#FF8A8A]">{bitcoinAdvisoryError}</p>
              ) : bitcoinAdvisory?.crypto_data?.length ? (
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={bitcoinAdvisory.crypto_data}>
                    <defs>
                      <linearGradient id="cryptoGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#B794F6" />
                        <stop offset="100%" stopColor="#FFD700" />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="time"
                      stroke="#8B92A8"
                      style={{ fontSize: "12px" }}
                    />
                    <YAxis stroke="#8B92A8" style={{ fontSize: "12px" }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(30, 34, 42, 0.9)",
                        border: "1px solid rgba(255, 255, 255, 0.1)",
                        borderRadius: "8px",
                        color: "#E8EDF3",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="url(#cryptoGradient)"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-[#8B92A8]">Loading Bitcoin model data from backend...</p>
              )}
              <div className="mt-4 flex items-center justify-center">
                <motion.div
                  animate={{
                    boxShadow: [
                      "0 0 20px rgba(255, 215, 0, 0.5)",
                      "0 0 40px rgba(183, 148, 246, 0.7)",
                      "0 0 20px rgba(255, 215, 0, 0.5)",
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="px-6 py-2 bg-gradient-to-r from-[#B794F6] to-[#FFD700] rounded-full text-[#121418]"
                >
                  <span className="flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    <span>{bitcoinAdvisory?.bitcoin_signal_label || "Loading BTC Signal..."}</span>
                  </span>
                </motion.div>
              </div>
              {bitcoinAdvisory && (
                <p className="mt-3 text-center text-xs text-[#8B92A8]">
                  Source: {bitcoinAdvisory.model_source} | Trend: {bitcoinAdvisory.bitcoin_trend}
                </p>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}