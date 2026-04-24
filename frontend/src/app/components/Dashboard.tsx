import { useLocation, useNavigate } from "react-router";
import { motion } from "motion/react";
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
import type { AdvisoryResponse } from "../lib/api";

const fdRankings = [
  { bank: "SBI Fixed Deposit", rate: 7.1, amount: 500000, progress: 90 },
  { bank: "HDFC Bank FD", rate: 7.0, amount: 300000, progress: 85 },
  { bank: "ICICI Flexi FD", rate: 6.9, amount: 200000, progress: 80 },
  { bank: "Axis Bank FD", rate: 6.8, amount: 150000, progress: 75 },
  { bank: "Kotak Mahindra FD", rate: 6.7, amount: 100000, progress: 70 },
];

const cryptoData = [
  { time: "00:00", price: 42000 },
  { time: "04:00", price: 43200 },
  { time: "08:00", price: 41800 },
  { time: "12:00", price: 44500 },
  { time: "16:00", price: 45200 },
  { time: "20:00", price: 46800 },
  { time: "Now", price: 47500 },
];

export function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const userData = location.state?.userData;
  const advisoryResponse = location.state?.advisoryResponse as AdvisoryResponse | undefined;
  const epfHealth = Math.max(
    0,
    Math.min(
      100,
      100 - Number(advisoryResponse?.epf_analysis?.deficit_percentage ?? 15),
    ),
  );

  const epfData = [{ name: "EPF Health", value: epfHealth, fill: "#3EFFA3" }];

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
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-7"
          >
            <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl h-full">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-[rgba(0,212,255,0.1)] rounded-lg">
                  <DollarSign className="w-6 h-6 text-[#00D4FF]" />
                </div>
                <h2 className="text-2xl text-[#E8EDF3]">FD Rankings</h2>
              </div>
              <div className="space-y-4">
                {fdRankings.map((fd, index) => (
                  <motion.div
                    key={fd.bank}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="group hover:bg-[rgba(0,212,255,0.05)] p-4 rounded-xl transition-all duration-300 border border-transparent hover:border-[rgba(0,212,255,0.3)]"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-[#E8EDF3]">{fd.bank}</h3>
                        <p className="text-sm text-[#8B92A8]">
                          ₹{fd.amount.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl text-[#00D4FF]">{fd.rate}%</div>
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
                <div className="p-2 bg-[rgba(62,255,163,0.1)] rounded-lg">
                  <Shield className="w-6 h-6 text-[#3EFFA3]" />
                </div>
                <h2 className="text-2xl text-[#E8EDF3]">EPF Health</h2>
              </div>
              <div className="flex items-center justify-center h-64">
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
                    <RadialBar
                      background
                      dataKey="value"
                      cornerRadius={10}
                      fill="#3EFFA3"
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute text-center">
                  <div className="text-5xl text-[#3EFFA3]">{Math.round(epfHealth)}%</div>
                  <p className="text-sm text-[#8B92A8] mt-1">
                    {advisoryResponse?.epf_analysis?.status || "Optimal"}
                  </p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="p-3 bg-[rgba(62,255,163,0.05)] rounded-lg border border-[rgba(62,255,163,0.2)]">
                  <p className="text-xs text-[#8B92A8]">Balance</p>
                  <p className="text-xl text-[#3EFFA3] mt-1">
                    ₹{userData?.currentEPF?.toLocaleString() || "500,000"}
                  </p>
                </div>
                <div className="p-3 bg-[rgba(62,255,163,0.05)] rounded-lg border border-[rgba(62,255,163,0.2)]">
                  <p className="text-xs text-[#8B92A8]">Growth</p>
                  <p className="text-xl text-[#3EFFA3] mt-1">
                    {advisoryResponse?.epf_analysis?.priority_level || "No Priority"}
                  </p>
                </div>
              </div>
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
                    <p className="text-sm text-[#8B92A8]">BTC/USD - 24H Trend</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl bg-gradient-to-r from-[#B794F6] to-[#FFD700] bg-clip-text text-transparent">
                    $47,500
                  </div>
                  <div className="flex items-center gap-1 text-[#3EFFA3] text-sm mt-1">
                    <TrendingUp className="w-4 h-4" />
                    <span>+8.2%</span>
                  </div>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={cryptoData}>
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
                    <span>BUY Signal Active</span>
                  </span>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
