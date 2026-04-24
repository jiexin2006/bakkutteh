export type AdvisoryRequest = {
  name: string;
  age: number;
  salary: number;
  monthlyExpenses: number;
  currentFD: number;
  currentEPF: number;
  cryptoHoldings: number;
  fixedLiabilities?: number;
  riskAppetite?: string;
  epfDeductionRm?: number;
  targetRetirementTier?: string;
};

export type AdvisoryAction = {
  percentage: string;
  category: string;
  action: string;
  reasoning: string;
};

export type AdvisoryResponse = {
  request_id?: string;
  advisory_source?: "zai" | "fallback";
  advisory_label?: "LIVE_ZAI" | "TEMPORARY_FALLBACK";
  advisory_error?: string | null;
  user_profile: Record<string, unknown>;
  epf_analysis: {
    status: string;
    deficit_percentage: number;
    priority_level: string;
    selected_target_rm: number;
    deficit_rm: number;
  };
  market_signals: {
    bitcoin_signal: string;
    bitcoin_confidence: number;
    bitcoin_trend: string;
  };
  advisory_json: {
    overall_strategy?: string;
    safety_gauge?: string;
    action_plan?: AdvisoryAction[];
    next_step?: string;
  };
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://127.0.0.1:8000";

function createRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `req-${Date.now()}-${Math.floor(Math.random() * 100000)}`;
}

export async function fetchAdvisory(payload: AdvisoryRequest): Promise<AdvisoryResponse> {
  const requestId = createRequestId();
  const startedAt = performance.now();
  console.info(`[advisory:${requestId}] sending request`, payload);

  const response = await fetch(`${API_BASE_URL}/api/advisory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-request-id": requestId,
    },
    body: JSON.stringify(payload),
  });

  const elapsedMs = Math.round(performance.now() - startedAt);
  console.info(`[advisory:${requestId}] response status ${response.status} in ${elapsedMs}ms`);

  if (!response.ok) {
    let detail = "Failed to fetch advisory";
    try {
      const errorPayload = await response.json();
      const payloadDetail = errorPayload?.detail;
      if (Array.isArray(payloadDetail) && payloadDetail.length > 0) {
        const firstError = payloadDetail[0];
        const fieldPath = Array.isArray(firstError?.loc)
          ? firstError.loc.join(".")
          : "request";
        detail = `${fieldPath}: ${firstError?.msg || "Invalid input"}`;
      } else if (typeof payloadDetail === "string") {
        detail = payloadDetail;
      }
    } catch {
      // Keep default detail if error payload is not JSON.
    }
    console.error(`[advisory:${requestId}] request failed`, detail);
    throw new Error(detail);
  }

  const data = (await response.json()) as AdvisoryResponse;
  console.info(`[advisory:${requestId}] parsed advisory response`, {
    requestIdFromServer: data.request_id,
    hasActionPlan: Array.isArray(data?.advisory_json?.action_plan),
  });
  return data;
}
