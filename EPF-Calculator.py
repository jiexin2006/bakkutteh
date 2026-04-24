import json
from typing import Dict, Tuple

class EPFAnalysisCalculator:
    def __init__(self, epf_standards_path: str = "epf-standards.json"):
        """
        Initialize the EPF Analysis Calculator
        
        Args:
            epf_standards_path: Path to epf-standards.json file
        """
        with open(epf_standards_path, "r") as f:
            self.epf_standards = json.load(f)
        self.standards_list = self.epf_standards["epf_standards_by_age"]
    
    def lookup_epf_standards(self, user_age: int) -> Dict[str, int]:
        """
        Step 1: Look up EPF standards for user's age
        
        Args:
            user_age: User's current age
        
        Returns:
            Dictionary with basic_target_rm, adequate_target_rm, enhanced_target_rm
        """
        # Try exact age match
        for standard in self.standards_list:
            if standard["age"] == user_age:
                return {
                    "basic_target_rm": standard["basic_rm"],
                    "adequate_target_rm": standard["adequate_rm"],
                    "enhanced_target_rm": standard["enhanced_rm"]
                }
        
        # If exact age not found, use closest age
        closest = min(self.standards_list, key=lambda x: abs(x["age"] - user_age))
        return {
            "basic_target_rm": closest["basic_rm"],
            "adequate_target_rm": closest["adequate_rm"],
            "enhanced_target_rm": closest["enhanced_rm"]
        }
    
    def select_target(self, epf_standards: Dict[str, int], target_epf_level: str) -> int:
        """
        Step 2: Select target based on user's chosen level
        
        Args:
            epf_standards: Dictionary from lookup_epf_standards
            target_epf_level: "basic", "adequate", or "enhanced"
        
        Returns:
            Selected target amount in RM
        """
        level_map = {
            "basic": "basic_target_rm",
            "adequate": "adequate_target_rm",
            "enhanced": "enhanced_target_rm"
        }
        
        key = level_map.get(target_epf_level.lower())
        if not key:
            raise ValueError(f"Invalid target_epf_level: {target_epf_level}. Must be basic, adequate, or enhanced.")
        
        return epf_standards[key]
    
    def calculate_deficit_rm(self, selected_target_rm: int, current_epf_balance_rm: int) -> int:
        """
        Step 3: Calculate EPF deficit in RM
        
        Args:
            selected_target_rm: Target amount
            current_epf_balance_rm: Current EPF balance
        
        Returns:
            Deficit in RM (negative = surplus)
        """
        return selected_target_rm - current_epf_balance_rm
    
    def calculate_deficit_percentage(self, deficit_rm: int, selected_target_rm: int) -> float:
        """
        Step 4: Calculate deficit as percentage
        
        Args:
            deficit_rm: Deficit amount in RM
            selected_target_rm: Target amount
        
        Returns:
            Deficit percentage (negative = surplus)
        """
        if selected_target_rm == 0:
            return 0
        return (deficit_rm / selected_target_rm) * 100
    
    def determine_status(self, deficit_rm: int) -> str:
        """
        Step 5: Determine EPF status
        
        Args:
            deficit_rm: Deficit amount in RM
        
        Returns:
            "On Track" or "Behind"
        """
        return "On Track" if deficit_rm <= 0 else "Behind"
    
    def determine_priority_level(self, deficit_percentage: float) -> Tuple[str, str]:
        """
        Step 6: Determine priority level based on deficit percentage
        
        Args:
            deficit_percentage: Deficit percentage
        
        Returns:
            Tuple of (priority_level, reasoning_rule_id)
        """
        if deficit_percentage >= 75:
            return "Critical", "critical_deficit"
        elif deficit_percentage >= 50:
            return "High", "high_deficit"
        elif deficit_percentage >= 25:
            return "Medium", "medium_deficit"
        elif deficit_percentage > 0:
            return "Low", "low_deficit"
        else:
            return "No Priority", "on_track"
    
    def calculate_epf_analysis(
        self,
        user_age: int,
        current_epf_balance_rm: int,
        target_epf_level: str
    ) -> Dict:
        """
        Main function: Calculate complete EPF analysis
        
        Args:
            user_age: User's current age (18-60)
            current_epf_balance_rm: User's current EPF balance
            target_epf_level: Target tier ("basic", "adequate", "enhanced")
        
        Returns:
            Dictionary containing:
            - age
            - current_balance_rm
            - target_level
            - basic_target_rm
            - adequate_target_rm
            - enhanced_target_rm
            - selected_target_rm
            - deficit_rm
            - deficit_percentage
            - status
            - priority_level
            - reasoning_rule_id
        """
        # Validate inputs
        if not (18 <= user_age <= 60):
            raise ValueError(f"Age must be between 18 and 60, got {user_age}")
        if current_epf_balance_rm < 0:
            raise ValueError(f"EPF balance cannot be negative, got {current_epf_balance_rm}")
        if target_epf_level.lower() not in ["basic", "adequate", "enhanced"]:
            raise ValueError(f"Invalid target level: {target_epf_level}")
        
        # Step 1: Look up EPF standards
        epf_standards = self.lookup_epf_standards(user_age)
        
        # Step 2: Select target
        selected_target_rm = self.select_target(epf_standards, target_epf_level)
        
        # Step 3: Calculate deficit in RM
        deficit_rm = self.calculate_deficit_rm(selected_target_rm, current_epf_balance_rm)
        
        # Step 4: Calculate deficit percentage
        deficit_percentage = self.calculate_deficit_percentage(deficit_rm, selected_target_rm)
        
        # Step 5: Determine status
        status = self.determine_status(deficit_rm)
        
        # Step 6: Determine priority level
        priority_level, reasoning_rule_id = self.determine_priority_level(deficit_percentage)
        
        # Compile and return analysis
        analysis = {
            "age": user_age,
            "current_balance_rm": current_epf_balance_rm,
            "target_level": target_epf_level.lower(),
            "basic_target_rm": epf_standards["basic_target_rm"],
            "adequate_target_rm": epf_standards["adequate_target_rm"],
            "enhanced_target_rm": epf_standards["enhanced_target_rm"],
            "selected_target_rm": selected_target_rm,
            "deficit_rm": deficit_rm,
            "deficit_percentage": round(deficit_percentage, 2),
            "status": status,
            "priority_level": priority_level,
            "reasoning_rule_id": reasoning_rule_id
        }
        
        return analysis


# Usage examples and testing
if __name__ == "__main__":
    # Initialize calculator
    calculator = EPFAnalysisCalculator("epf-standards.json")
    
    # Example 1: The Struggling Student (U001)
    print("=" * 60)
    print("Example 1: The Struggling Student (U001)")
    print("=" * 60)
    
    analysis1 = calculator.calculate_epf_analysis(
        user_age=21,
        current_epf_balance_rm=500,
        target_epf_level="basic"
    )
    
    print(json.dumps(analysis1, indent=2))
    print()
    
    # Example 2: The Ideal Target (U004)
    print("=" * 60)
    print("Example 2: The Ideal Target (U004)")
    print("=" * 60)
    
    analysis2 = calculator.calculate_epf_analysis(
        user_age=28,
        current_epf_balance_rm=35000,
        target_epf_level="basic"
    )
    
    print(json.dumps(analysis2, indent=2))
    print()
    
    # Example 3: The Aggressive Wealth Builder (U005)
    print("=" * 60)
    print("Example 3: The Aggressive Wealth Builder (U005)")
    print("=" * 60)
    
    analysis3 = calculator.calculate_epf_analysis(
        user_age=30,
        current_epf_balance_rm=65000,
        target_epf_level="enhanced"
    )
    
    print(json.dumps(analysis3, indent=2))