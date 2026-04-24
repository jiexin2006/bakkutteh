from advisor_logic import final_advisor_logic

# Scenario 1: Market is booming (+15%), but User is "Behind" on EPF
print("Scenario 1 (Safety Check):")
print(final_advisor_logic(0.15, "Behind")) 
# EXPECTED: Should tell user to stay safe/invest very little.

# Scenario 2: Market is booming (+15%), and User is "On Track"
print("\nScenario 2 (Growth Check):")
print(final_advisor_logic(0.15, "On Track"))
# EXPECTED: Should give a green light for Bitcoin (e.g., 20%).

# Scenario 3: Market is crashing (-10%), even if User is "On Track"
print("\nScenario 3 (Market Risk Check):")
print(final_advisor_logic(-0.10, "On Track"))
# EXPECTED: Should tell user to hold in FD/Cash.