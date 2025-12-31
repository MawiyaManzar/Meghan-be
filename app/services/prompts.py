"""
System Instructions and Prompt Template Generation
Generates dynamic system instructions for the Meghan chatbot based on user context.
"""
from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


def generate_system_instructions(
    tier: str,
    mood: str,
    source: str,
    bio: Optional[Dict[str, Any]] = None,
    other_text: Optional[str] = None
) -> str:
    """
    Generate system instructions for the chatbot based on user context.
    
    Args:
        tier: Risk tier ('Green', 'Yellow', 'Red')
        mood: Current mood ('Heavy', 'Pulse', 'Grounded')
        source: Stress source ('Family', 'Relationship', 'Career/Academics', 'Others')
        bio: Optional dict with user bio info (name, major, hobbies, values, bio)
        other_text: Optional text when source is 'Others'
    
    Returns:
        Formatted system instructions string
    """
    # Build user context section
    user_context_parts = []
    
    if bio:
        if bio.get("name"):
            user_context_parts.append(f"Name: {bio['name']}")
        if bio.get("major"):
            user_context_parts.append(f"Major: {bio['major']}")
        if bio.get("hobbies"):
            user_context_parts.append(f"Hobbies: {bio['hobbies']}")
        if bio.get("values"):
            user_context_parts.append(f"Values: {bio['values']}")
        if bio.get("bio"):
            user_context_parts.append(f"About: {bio['bio']}")
    
    user_context = "\n".join(user_context_parts) if user_context_parts else "No additional user information provided."
    
    # Build stress context
    stress_context = f"Current stress source: {source}"
    if source == "Others" and other_text:
        stress_context += f" - {other_text}"
    
    # Mood descriptions
    mood_descriptions = {
        "Heavy": "feeling heavy, sad, or down",
        "Pulse": "feeling anxious, worried, or on edge",
        "Grounded": "feeling calm, balanced, or stable"
    }
    mood_desc = mood_descriptions.get(mood, mood.lower())
    
    # Tier-specific guidance
    tier_guidance = {
        "Green": (
            "The user is in a stable emotional state. Provide supportive, "
            "encouraging responses. You can engage in casual conversation and "
            "wellness tips. Maintain a warm, friendly tone."
        ),
        "Yellow": (
            "The user is experiencing moderate stress. Be empathetic and attentive. "
            "Focus on validation, coping strategies, and support. Monitor for any "
            "escalation in distress. Suggest practical wellness activities."
        ),
        "Red": (
            "The user is in a high-risk emotional state. Prioritize safety and "
            "immediate support. Be compassionate, validate their feelings, and "
            "provide crisis resources if needed. Focus on immediate coping strategies "
            "and consider suggesting professional support."
        )
    }
    tier_guidance_text = tier_guidance.get(tier, tier_guidance["Yellow"])
    
    # Construct system instructions
    system_instructions = f"""You are Meghan, an empathetic and supportive wellness assistant designed to help university students navigate stress and mental health challenges.

Your primary role is to provide compassionate, personalized support based on the user's current emotional state and context.

USER CONTEXT:
{user_context}

CURRENT STATE:
- Emotional state: The user is currently {mood_desc} (mood: {mood})
- {stress_context}
- Risk level: {tier}

RESPONSE GUIDELINES:
{tier_guidance_text}

IMPORTANT GUIDELINES:
1. Always maintain an empathetic, non-judgmental tone
2. Validate the user's feelings and experiences
3. Provide practical, actionable advice when appropriate
4. Respect the user's autonomy and choices
5. Encourage self-care and wellness practices
6. If the user mentions self-harm or crisis situations, provide appropriate resources and support
7. Keep responses conversational and natural, not clinical or robotic
8. Use the user's context (name, major, hobbies, values) to personalize your responses when relevant
9. Be concise but warm - aim for helpful, supportive responses without being overly verbose

Remember: You are here to support, not to diagnose or replace professional mental health care. Always prioritize the user's wellbeing and safety.
"""
    
    return system_instructions


def create_chat_prompt_template() -> ChatPromptTemplate:
    """
    Create a LangChain ChatPromptTemplate for the chat interface.
    
    Returns:
        ChatPromptTemplate configured for system + human messages
    """
    system_template = SystemMessagePromptTemplate.from_template("{system_instructions}")
    human_template = HumanMessagePromptTemplate.from_template("{human_input}")
    
    prompt = ChatPromptTemplate.from_messages([
        system_template,
        human_template
    ])
    
    return prompt


def format_chat_history(messages: list) -> list:
    """
    Format chat history for LangChain from list of dicts with 'role' and 'content'.
    
    Args:
        messages: List of message dicts with keys 'role' ('user' or 'model') and 'content'
    
    Returns:
        List of LangChain message objects (HumanMessage or AIMessage)
    """
    from langchain_core.messages import HumanMessage, AIMessage
    
    formatted = []
    for msg in messages:
        role = msg.get("role", "").lower()
        content = msg.get("content", "")
        
        if role == "user":
            formatted.append(HumanMessage(content=content))
        elif role == "model" or role == "assistant":
            formatted.append(AIMessage(content=content))
        # Skip unknown roles
    
    return formatted

