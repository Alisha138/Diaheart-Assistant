def get_recommendations(risk_score: float, health_category: str) -> dict:
    """
    Generates personalized, empathy-driven lifestyle advice based on medical risk scores.
    
    Args:
        risk_score (float): The percentage of risk (0 to 100).
        health_category (str): The medical category (e.g., 'Diabetes', 'Cardiovascular').
        
    Returns:
        dict: A structured response containing the title, lifestyle shift, 
              nutritional focus, doctor consultation advice, and safety disclaimer.
    """
    # Mandatory disclaimer applied to all responses
    disclaimer = "This is for educational purposes only and not a substitute for professional medical diagnosis."
    is_diabetes = "diabet" in health_category.lower()
    
    # Categorize risk levels
    if risk_score <= 30:
        level = "Low"
    elif risk_score <= 60:
        level = "Moderate"
    else:
        level = "High"
        
    # Diabetes Recommendations
    if is_diabetes:
        if level == "Low":
            title = "Fantastic Baseline! Let's Keep the Momentum Going "
            lifestyle = "Try adding a gentle 15-minute walk after your heaviest meal of the day to help your body naturally process energy efficiently."
            nutrition = "Keep enjoying your meals, but consider swapping out white bread for a hearty whole-grain option to give your body a steady fuel release."
            doctor = "Continue your routine check-ups. If you ever find yourself feeling unusually thirsty or fatigued for several days, it's worth checking with your GP."
            
        elif level == "Moderate":
            title = "Recommendations"
            lifestyle = "Focus on adding movements and mild exercises which significantly boost your metabolic health! try doing a 10-minute daily walk after meals to kep the metabolism smooth."
            nutrition = "Try a handful of unsalted nuts instead of sugary snacks when you need an afternoon boost. Avoid sugary items on empty stomach or early in the morning. Adding ginger tea in the morning is a plus point"
            doctor = "It's a good idea to schedule a non-urgent visit with your doctor in the near future just to review your routine blood work and stay ahead."
            
        else: # High
            title = "Your Health is a Priority: Let's Take Protective Steps Together "
            lifestyle = "Small, consistent steps make the biggest difference. Start by committing to 10 minutes of light stretching or yoga daily to improve circulation and reduce stress."
            nutrition = "Focus heavily on colorful veggies and lean proteins; replacing sugary drinks with infused water or unsweetened tea is a massive step forward for your metabolism. Completely avoid added sugars."
            doctor = "To give yourself peace of mind, please schedule a follow-up with your Doctor soon to collaborate on a safe, actionable health  plan."
            
    # Cardiovascular (Heart) Recommendations
    else: 
        if level == "Low":
            title = "Strong Heart Beats! Keep Up the Great Work "
            lifestyle = "Think of your heart like a battery that needs steady recharge. Ensure you are getting 7-8 hours of quality sleep to let it rest optimally."
            nutrition = "Sprinkle some heart-loving chia or flax seeds into your morning oatmeal or yogurt for an easy, delicious omega-3 boost."
            doctor = "No immediate concerns! Stick to your annual physician visits, but if you ever experience persistent unusual dizziness, bring it up with your GP."
            
        elif level == "Moderate":
            title = "Recommendations "
            lifestyle = "Focusing on these small changes can significantly boost your heart health. Try parking a bit further away to sneak in some extra restorative steps each day."
            nutrition = "Experiment with swapping out some salt for flavorful, vibrant herbs and spices like garlic, turmeric, or oregano when cooking dinner."
            doctor = "It's worth having a friendly chat with your GP during your next visit about your blood pressure and cholesterol numbers just to keep them optimized."
            
        else: # High
            title = "Empower Your Heart: Steps You Can Take Today "
            lifestyle = "Your heart is resilient! A wonderful way to support it right now is by practicing 5 minutes of deep, calming breathing exercises every morning to lower physical stress."
            nutrition = "Try focusing on potassium-rich foods like bananas or spinach, and steer clear of heavily processed or fried meals to make things immensely easier on your heart."
            doctor = "It's highly encouraged to book an appointment with your doctor soon. They can be your best partner in creating a safe, comfortable cardiovascular action plan."

    # Return structured JSON-friendly dictionary
    return {
        "Title": title,
        "Lifestyle Shift": lifestyle,
        "Nutritional Focus": nutrition,
        "When to see a Doctor": doctor,
        "Safety Disclaimer": disclaimer
    }
