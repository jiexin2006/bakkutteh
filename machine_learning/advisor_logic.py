def final_advisor_logic(ml_prediction, user_epf_status):
    
    if user_epf_status == "Behind":
        if ml_prediction > 0.10: 
            return "ML is very bullish, but you are behind on EPF. Invest ONLY 5% in BTC."
        else:
            return "Priority: Safety. Move 100% of surplus to EPF/Fixed Deposit."
    
    else: 
        if ml_prediction > 0.02:
            return "ML Signal: BUY. Suggested allocation: 20% BTC."
        else:
            return "Market is sideways. Hold in FD for now."

# --- TEST BLOCK ---
# Let's pretend the AI predicts a 12% jump (0.12) 
# and the user is "Behind" their EPF target.
test_prediction = 0.12
test_status = "Behind"

result = final_advisor_logic(test_prediction, test_status)
print(f"Test Result: {result}")