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

export type UserData = {
  name: string;
  age: string;
  salary: string;
  monthlyExpenses: string;
  currentFD: string;
  currentEPF: string;
  cryptoHoldings: string;
};

export type AdvisoryAction = {
  percentage: string;
  category: string;
  action: string;
  reasoning: string;
};

export type FDRanking = {
  bank_name: string | null;
  account_type: string | null;
  tenure_months: number | null;
  interest_rate_pct: number | null;
  min_placement_rm: number | null;
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

export type FDRankingResponse = {
  epf_dividend_rate_pct: number;
  verified_market_rates: FDRanking[];
};

export type BitcoinAdvisoryPoint = {
  time: string;
  price: number;
};

export type BitcoinAdvisoryResponse = {
  bitcoin_signal: string;
  bitcoin_signal_label: string;
  bitcoin_confidence: number;
  bitcoin_trend: string;
  forecast_change_pct: number;
  forecast_price: number;
  current_price: number;
  current_price_myr: number;
  price_source: string;
  price_status: string;
  crypto_data: BitcoinAdvisoryPoint[];
  model_source: string;
};

export type SavedProfileResponse = {
  user_data: UserData | null;
};

export type SavedProfileItem = {
  id: string;
  name: string;
  saved_at: string;
  user_data: UserData;
};

export type ProfilesResponse = {
  active_profile_id: string | null;
  profiles: SavedProfileItem[];
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

export async function fetchFDRankings(limit = 6): Promise<FDRankingResponse> {
  const response = await fetch(`${API_BASE_URL}/api/fd-rankings?limit=${limit}`);

  if (!response.ok) {
    throw new Error("Failed to fetch FD rankings");
  }

  return (await response.json()) as FDRankingResponse;
}

export async function fetchBitcoinAdvisory(): Promise<BitcoinAdvisoryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/bitcoin-advisory`);

  if (!response.ok) {
    throw new Error("Failed to fetch Bitcoin advisory");
  }

  return (await response.json()) as BitcoinAdvisoryResponse;
}

export async function fetchSavedUserData(): Promise<UserData | null> {
  const response = await fetch(`${API_BASE_URL}/api/saved-profile`);
  if (!response.ok) {
    throw new Error("Failed to fetch saved profile");
  }
  const payload = (await response.json()) as SavedProfileResponse;
  return payload.user_data;
}

export async function saveUserData(userData: UserData): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/saved-profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_data: userData }),
  });

  if (!response.ok) {
    throw new Error("Failed to save profile");
  }
}

export async function fetchProfiles(): Promise<ProfilesResponse> {
  const response = await fetch(`${API_BASE_URL}/api/profiles`);

  if (!response.ok) {
    throw new Error("Failed to fetch profiles");
  }

  return (await response.json()) as ProfilesResponse;
}

export async function selectProfile(profileId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/profiles/select`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ profile_id: profileId }),
  });

  if (!response.ok) {
    throw new Error("Failed to select profile");
  }
}

export async function updateProfile(profileId: string, userData: UserData): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/profiles/${profileId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_data: userData }),
  });

  if (!response.ok) {
    throw new Error("Failed to update profile");
  }
}

export async function createProfile(userData: UserData): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/profiles`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_data: userData }),
  });

  if (!response.ok) {
    throw new Error("Failed to create profile");
  }

  const payload = (await response.json()) as { profile_id: string };
  return payload.profile_id;
}

export async function resetSavedUserData(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/saved-profile`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to reset saved profile");
  }
}
