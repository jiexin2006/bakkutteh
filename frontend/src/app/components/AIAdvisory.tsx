import { useNavigate } from "react-router";
import { motion } from "motion/react";
import {
  ArrowLeft,
  Brain,
  Target,
  TrendingUp,
  Shield,
  Coins,
  Sparkles,
} from "lucide-react";

const allocations = [
  {
    category: "Fixed Deposits",
    amount: 250000,
    percentage: 50,
    icon: Shield,
    color: "#00D4FF",
    bgColor: "rgba(0, 212, 255, 0.1)",
  },
  {
    category: "EPF Contribution",
    amount: 150000,
    percentage: 30,
    icon: Target,
    color: "#3EFFA3",
    bgColor: "rgba(62, 255, 163, 0.1)",
  },
  {
    category: "Crypto Assets",
    amount: 100000,
    percentage: 20,
    icon: Coins,
    color: "#FFD700",
    bgColor: "rgba(255, 215, 0, 0.1)",
  },
];

const strategies = [
  {
    priority: "1st Priority",
    title: "Maximize Fixed Deposit Returns",
    description:
      "Allocate ₹2,50,000 to SBI Fixed Deposit at 7.1% p.a. This provides stable, guaranteed returns with minimal risk exposure. The 90-day lock-in period aligns with your liquidity requirements.",
    reasoning: [
      "Highest rate among top-tier banks",
      "Government-backed security",
      "Tax benefits under 80C available",
      "Predictable cash flow generation",
    ],
    icon: Shield,
    gradient: "from-[#00D4FF] to-[#00A3CC]",
  },
  {
    priority: "2nd Priority",
    title: "Strategic Crypto Positioning",
    description:
      "Invest ₹1,00,000 in Bitcoin during the current accumulation phase. Technical indicators show strong buy signals with RSI at 45 and MACD crossover detected. Target 15-20% returns in Q2 2026.",
    reasoning: [
      "Market shows bullish reversal pattern",
      "Institutional accumulation detected",
      "Favorable risk-reward ratio (1:4)",
      "Portfolio diversification benefits",
    ],
    icon: TrendingUp,
    gradient: "from-[#B794F6] to-[#FFD700]",
  },
  {
    priority: "3rd Priority",
    title: "EPF Long-term Stability",
    description:
      "Maintain ₹1,50,000 annual EPF contribution for retirement corpus building. Current 8.15% interest rate combined with employer matching doubles your wealth creation velocity.",
    reasoning: [
      "Tax-free compound growth",
      "Employer contribution match",
      "Retirement security foundation",
      "Inflation-beating returns",
    ],
    icon: Target,
    gradient: "from-[#3EFFA3] to-[#00CC7A]",
  },
];

export function AIAdvisory() {
  const navigate = useNavigate();

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
          className="mb-8"
        >
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 text-[#8B92A8] hover:text-[#00D4FF] transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-[#B794F6] to-[#FFD700] rounded-xl">
              <Brain className="w-8 h-8 text-[#121418]" />
            </div>
            <div>
              <h1 className="text-4xl md:text-5xl tracking-tight bg-gradient-to-r from-[#B794F6] via-[#FFD700] to-[#00D4FF] bg-clip-text text-transparent">
                AI Advisory Strategy
              </h1>
              <p className="text-[#8B92A8] mt-1">
                Data-driven recommendations powered by quantum analysis
              </p>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-4"
          >
            <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl sticky top-6">
              <div className="flex items-center gap-2 mb-6">
                <Sparkles className="w-5 h-5 text-[#FFD700]" />
                <h2 className="text-2xl text-[#E8EDF3]">Allocated Amounts</h2>
              </div>
              <div className="space-y-4">
                {allocations.map((allocation, index) => (
                  <motion.div
                    key={allocation.category}
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="p-4 rounded-xl border transition-all duration-300 hover:scale-[1.02]"
                    style={{
                      backgroundColor: allocation.bgColor,
                      borderColor: `${allocation.color}40`,
                    }}
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{ backgroundColor: `${allocation.color}20` }}
                      >
                        <allocation.icon
                          className="w-5 h-5"
                          style={{ color: allocation.color }}
                        />
                      </div>
                      <h3 className="text-[#E8EDF3]">{allocation.category}</h3>
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span
                        className="text-3xl"
                        style={{ color: allocation.color }}
                      >
                        ₹{allocation.amount.toLocaleString()}
                      </span>
                      <span className="text-[#8B92A8] text-sm">
                        ({allocation.percentage}%)
                      </span>
                    </div>
                    <div className="mt-3 h-2 bg-[rgba(255,255,255,0.05)] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${allocation.percentage}%` }}
                        transition={{ delay: 0.6 + index * 0.1, duration: 0.8 }}
                        className="h-full rounded-full"
                        style={{
                          background: `linear-gradient(90deg, ${allocation.color}, ${allocation.color}CC)`,
                        }}
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
              <div className="mt-6 p-4 bg-[rgba(255,255,255,0.03)] rounded-xl border border-[rgba(255,255,255,0.1)]">
                <p className="text-sm text-[#8B92A8] mb-2">Total Portfolio</p>
                <p className="text-3xl text-[#E8EDF3]">₹5,00,000</p>
                <div className="mt-3 flex items-center gap-2 text-[#3EFFA3] text-sm">
                  <TrendingUp className="w-4 h-4" />
                  <span>Expected Annual Return: 9.2%</span>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-8"
          >
            <div className="space-y-6">
              <div className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl">
                <h2 className="text-2xl text-[#E8EDF3] mb-2">AI Reasoning</h2>
                <p className="text-[#8B92A8] text-sm mb-6">
                  Strategic allocation optimized for risk-adjusted returns
                </p>
              </div>

              {strategies.map((strategy, index) => (
                <motion.div
                  key={strategy.priority}
                  initial={{ y: 30, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.5 + index * 0.15 }}
                  className="backdrop-blur-xl bg-[rgba(30,34,42,0.4)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 shadow-2xl hover:border-[rgba(255,255,255,0.2)] transition-all duration-300"
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`p-3 rounded-xl bg-gradient-to-br ${strategy.gradient}`}
                    >
                      <strategy.icon className="w-6 h-6 text-[#121418]" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs bg-gradient-to-r ${strategy.gradient} text-[#121418]`}
                        >
                          {strategy.priority}
                        </span>
                        <h3 className="text-xl text-[#E8EDF3]">
                          {strategy.title}
                        </h3>
                      </div>
                      <p className="text-[#8B92A8] mb-4 leading-relaxed">
                        {strategy.description}
                      </p>
                      <div className="space-y-2">
                        {strategy.reasoning.map((reason, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ x: -10, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.7 + index * 0.15 + idx * 0.05 }}
                            className="flex items-start gap-2 text-sm text-[#E8EDF3]"
                          >
                            <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-[#00D4FF] to-[#3EFFA3] mt-1.5" />
                            <span>{reason}</span>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
