# Risk Tier Inference Strategies for Journal Entries
## Senior Solutions Architect Analysis

## Executive Summary

This document outlines multiple strategies for automatically inferring `tier_at_time` (risk tier: Green/Yellow/Red) from journal entry content. Each strategy is evaluated for accuracy, performance, cost, and implementation complexity.

---

## Strategy 1: Enhanced Keyword-Based Classification (Recommended for MVP)

### Overview
Extend the existing `SafetyService` pattern with a multi-tier keyword/phrase classification system.

### Implementation Approach

```python
# app/services/tier_classifier.py

class TierClassifier:
    """
    Classifies journal content into risk tiers using keyword/phrase matching.
    """
    
    # RED tier indicators (crisis-level)
    RED_PATTERNS = [
        r"\bkill myself\b",
        r"\bsuicide\b",
        r"\bend my life\b",
        r"\bdon't want to live\b",
        r"\bwant to die\b",
        r"\bself harm\b",
        r"\bhurt myself\b",
        r"\bno way out\b",
        r"\bhopeless\b",
        r"\bworthless\b",
        # Add more patterns
    ]
    
    # YELLOW tier indicators (concerning but not crisis)
    YELLOW_PATTERNS = [
        r"\boverwhelmed\b",
        r"\bcan't cope\b",
        r"\bstruggling\b",
        r"\bexhausted\b",
        r"\banxious\b",
        r"\bpanic\b",
        r"\bworried\b",
        r"\bstressed\b",
        r"\bdepressed\b",
        r"\blonely\b",
        r"\bisolated\b",
        # Add more patterns
    ]
    
    # GREEN tier indicators (positive/neutral)
    GREEN_PATTERNS = [
        r"\bgrateful\b",
        r"\bhappy\b",
        r"\bexcited\b",
        r"\bcontent\b",
        r"\bpeaceful\b",
        r"\bcalm\b",
        r"\bgood day\b",
        r"\bprogress\b",
        # Add more patterns
    ]
    
    def classify(self, text: str) -> str:
        """
        Classify journal entry into risk tier.
        Returns: "Red", "Yellow", or "Green"
        """
        normalized = (text or "").lower().strip()
        
        # Check RED first (highest priority)
        for pattern in self.RED_PATTERNS:
            if re.search(pattern, normalized):
                return "Red"
        
        # Check YELLOW
        yellow_matches = sum(1 for p in self.YELLOW_PATTERNS if re.search(p, normalized))
        if yellow_matches >= 2:  # Multiple concerning indicators
            return "Yellow"
        
        # Check GREEN
        green_matches = sum(1 for p in self.GREEN_PATTERNS if re.search(p, normalized))
        if green_matches >= 2:  # Multiple positive indicators
            return "Green"
        
        # Default to YELLOW if mixed signals or neutral
        if yellow_matches > 0:
            return "Yellow"
        
        # Default to GREEN if no concerning indicators
        return "Green"
```

### Pros
- ✅ **Fast**: O(n) regex matching, <10ms per entry
- ✅ **No external dependencies**: Uses existing infrastructure
- ✅ **Deterministic**: Same input = same output (testable)
- ✅ **Low cost**: No API calls
- ✅ **Privacy-friendly**: No data leaves your system
- ✅ **Easy to maintain**: Pattern list can be updated by non-engineers

### Cons
- ❌ **Limited context understanding**: Misses nuanced language
- ❌ **False positives/negatives**: May misclassify sarcasm, metaphors
- ❌ **Requires maintenance**: Pattern list needs regular updates
- ❌ **Language-specific**: Only works for English (initially)

### Accuracy Estimate
- **Red detection**: ~85-90% (high precision, some false positives)
- **Yellow detection**: ~70-75% (moderate accuracy)
- **Green detection**: ~80-85% (good for positive content)

### Implementation Effort
- **Time**: 2-3 days
- **Complexity**: Low
- **Dependencies**: None (uses existing `SafetyService` pattern)

---

## Strategy 2: LLM-Based Classification (Recommended for Production)

### Overview
Use Gemini API (already integrated) to analyze journal content and classify risk tier.

### Implementation Approach

```python
# app/services/tier_classifier.py

class LLMTierClassifier:
    """
    Uses LLM to classify journal content into risk tiers.
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    async def classify(self, text: str) -> str:
        """
        Classify journal entry using LLM.
        Returns: "Red", "Yellow", or "Green"
        """
        prompt = f"""Analyze the following journal entry and classify the emotional risk level.

Journal Entry:
{text}

Classify into ONE of these risk tiers:
- Red: Crisis-level indicators (self-harm, suicide ideation, severe distress)
- Yellow: Concerning but manageable (stress, anxiety, overwhelm, sadness)
- Green: Neutral or positive (gratitude, contentment, normal challenges)

Respond with ONLY the tier name: Red, Yellow, or Green"""

        try:
            llm = self.llm_service.get_llm(temperature=0.1)  # Low temp for consistency
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            tier = response.content.strip().capitalize()
            
            # Validate response
            if tier in ["Red", "Yellow", "Green"]:
                return tier
            else:
                # Fallback to keyword-based if LLM returns invalid
                return self._fallback_classify(text)
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return self._fallback_classify(text)  # Graceful degradation
    
    def _fallback_classify(self, text: str) -> str:
        """Fallback to keyword-based classification"""
        keyword_classifier = TierClassifier()
        return keyword_classifier.classify(text)
```

### Pros
- ✅ **High accuracy**: ~90-95% for nuanced understanding
- ✅ **Context-aware**: Understands sarcasm, metaphors, context
- ✅ **Multilingual**: Can handle multiple languages (with proper prompts)
- ✅ **Adaptive**: Learns from patterns without code changes
- ✅ **Already integrated**: Uses existing Gemini infrastructure

### Cons
- ❌ **Cost**: ~$0.0001-0.0005 per classification (Gemini pricing)
- ❌ **Latency**: 200-500ms per classification (API call)
- ❌ **Non-deterministic**: Same input may yield different output (mitigated with low temperature)
- ❌ **Privacy concerns**: Content sent to external API (check Gemini's data policy)
- ❌ **Rate limiting**: Subject to API rate limits

### Accuracy Estimate
- **Red detection**: ~92-95%
- **Yellow detection**: ~88-92%
- **Green detection**: ~90-93%

### Implementation Effort
- **Time**: 3-5 days
- **Complexity**: Medium
- **Dependencies**: Existing `llm_service`

### Cost Analysis
- **Per journal entry**: ~$0.0002 (Gemini Flash)
- **10,000 entries/month**: ~$2/month
- **100,000 entries/month**: ~$20/month

---

## Strategy 3: Hybrid Approach (Recommended for Scale)

### Overview
Combine keyword-based (fast path) with LLM (fallback for uncertain cases).

### Implementation Approach

```python
class HybridTierClassifier:
    """
    Hybrid classifier: keyword-based for clear cases, LLM for ambiguous.
    """
    
    def __init__(self, keyword_classifier, llm_classifier):
        self.keyword = keyword_classifier
        self.llm = llm_classifier
    
    async def classify(self, text: str) -> str:
        """
        Fast keyword classification, LLM fallback for edge cases.
        """
        # Fast path: keyword classification
        keyword_tier = self.keyword.classify(text)
        confidence = self.keyword.get_confidence(text)
        
        # Use LLM only if confidence is low or result is ambiguous
        if confidence < 0.7 or keyword_tier == "Yellow":
            # Yellow is often ambiguous, use LLM for better accuracy
            return await self.llm.classify(text)
        
        # High confidence keyword result
        return keyword_tier
```

### Pros
- ✅ **Best of both worlds**: Fast + accurate
- ✅ **Cost-effective**: ~70% reduction in LLM calls
- ✅ **High accuracy**: LLM handles edge cases
- ✅ **Low latency**: Most requests <10ms (keyword path)

### Cons
- ❌ **Complexity**: Two systems to maintain
- ❌ **Still has LLM costs**: For ambiguous cases

### Accuracy Estimate
- **Overall**: ~90-93% (combines strengths of both)

### Implementation Effort
- **Time**: 5-7 days
- **Complexity**: Medium-High
- **Dependencies**: Both keyword and LLM classifiers

---

## Strategy 4: Sentiment Analysis + Rule Engine

### Overview
Use pre-trained sentiment analysis model (e.g., VADER, TextBlob) combined with custom rules.

### Implementation Approach

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentTierClassifier:
    """
    Uses sentiment analysis + custom rules for tier classification.
    """
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def classify(self, text: str) -> str:
        """
        Classify using sentiment scores + keyword rules.
        """
        # Get sentiment scores
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']  # -1 (negative) to +1 (positive)
        
        # Check for crisis keywords first (RED)
        if self._has_crisis_keywords(text):
            return "Red"
        
        # Sentiment-based classification
        if compound <= -0.5:  # Very negative
            return "Yellow"  # Could be Red, but let keyword check handle that
        elif compound <= -0.2:  # Moderately negative
            return "Yellow"
        elif compound >= 0.2:  # Positive
            return "Green"
        else:  # Neutral
            return "Green"  # Default to safe
```

### Pros
- ✅ **Fast**: Local processing, no API calls
- ✅ **Good for sentiment**: Handles positive/negative well
- ✅ **Open source**: No licensing costs

### Cons
- ❌ **Limited context**: Doesn't understand mental health nuances
- ❌ **False positives**: "I'm not sad" might score negative
- ❌ **Requires model**: Need to add dependency (VADER, TextBlob)

### Accuracy Estimate
- **Overall**: ~75-80% (good for sentiment, poor for mental health context)

### Implementation Effort
- **Time**: 2-3 days
- **Complexity**: Low-Medium
- **Dependencies**: `vaderSentiment` or `textblob` package

---

## Strategy 5: Historical Pattern Matching

### Overview
Learn from user's historical journal entries and chat interactions to infer tier.

### Implementation Approach

```python
class HistoricalTierClassifier:
    """
    Uses user's historical patterns to infer tier.
    """
    
    def classify(self, text: str, user_id: int, db: Session) -> str:
        """
        Classify based on user's historical patterns.
        """
        # Get user's recent journal entries with known tiers
        recent_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.tier_at_time.isnot(None)
        ).order_by(JournalEntry.created_at.desc()).limit(10).all()
        
        # Get user's recent chat conversations with tiers
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(5).all()
        
        # Analyze patterns
        # (Simplified - could use ML for this)
        avg_tier = self._calculate_average_tier(recent_entries, recent_conversations)
        
        # Combine with keyword classification
        keyword_tier = keyword_classifier.classify(text)
        
        # Weighted decision
        if keyword_tier == "Red":
            return "Red"  # Always prioritize crisis detection
        elif avg_tier == "Red" and keyword_tier == "Yellow":
            return "Yellow"  # User has been in Red, but current entry is Yellow
        else:
            return keyword_tier
```

### Pros
- ✅ **Personalized**: Adapts to individual user patterns
- ✅ **Context-aware**: Uses user's own history

### Cons
- ❌ **Cold start problem**: No data for new users
- ❌ **Privacy concerns**: Requires storing historical data
- ❌ **Complexity**: Requires pattern analysis logic

### Accuracy Estimate
- **With history**: ~85-90%
- **New users**: Falls back to keyword/LLM

### Implementation Effort
- **Time**: 7-10 days
- **Complexity**: High
- **Dependencies**: Database queries, pattern analysis

---

## Recommended Implementation Roadmap

### Phase 1: MVP (Week 1-2)
**Strategy 1: Enhanced Keyword-Based Classification**
- Fast to implement
- No external dependencies
- Good enough for launch
- Can be improved iteratively

### Phase 2: Production (Month 2-3)
**Strategy 3: Hybrid Approach**
- Add LLM classification for ambiguous cases
- Maintain fast path for clear cases
- Optimize cost vs. accuracy

### Phase 3: Advanced (Month 4+)
**Strategy 5: Historical Pattern Matching**
- Add personalization layer
- Improve accuracy for returning users
- Use ML for pattern detection

---

## Implementation in Journal Router

```python
# app/routers/journal.py

from app.services.tier_classifier import TierClassifier

tier_classifier = TierClassifier()  # Or HybridTierClassifier

@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: JournalEntryCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Create a new journal entry.
    Automatically infers tier_at_time from content if not provided.
    """
    
    # Infer tier if not provided
    if payload.tier_at_time is None:
        # Use classifier to infer tier
        tier = await tier_classifier.classify(payload.content)
    else:
        tier = payload.tier_at_time
    
    # Use mood from payload if provided, otherwise None
    mood = payload.mood_at_time
    
    # Safety gate check
    safety = safety_service.assess_user_message(payload.content)
    if not safety.allowed:
        # Log crisis event
        # ... existing crisis logging code ...
        raise HTTPException(...)
    
    # Create entry
    entry = JournalEntry(
        user_id=current_user.id,
        content=payload.content,
        mood_at_time=mood,
        tier_at_time=tier,  # Now inferred if not provided
        xp_gained=HEARTS_FOR_JOURNAL,
    )
    
    # ... rest of the code ...
```

---

## Decision Matrix

| Strategy | Accuracy | Speed | Cost | Complexity | Privacy | Recommendation |
|----------|----------|-------|------|------------|---------|----------------|
| Keyword-Based | 75-85% | ⚡⚡⚡ | $0 | Low | ✅✅✅ | **MVP** |
| LLM-Based | 90-95% | ⚡⚡ | $0.0002/entry | Medium | ⚠️⚠️ | **Production** |
| Hybrid | 90-93% | ⚡⚡⚡ | $0.00006/entry | Medium-High | ⚠️⚠️ | **Scale** |
| Sentiment | 75-80% | ⚡⚡⚡ | $0 | Low-Medium | ✅✅✅ | Alternative |
| Historical | 85-90% | ⚡⚡ | $0 | High | ⚠️⚠️ | Future |

---

## Next Steps

1. **Immediate**: Implement Strategy 1 (Keyword-Based) for MVP
2. **Short-term**: Add Strategy 3 (Hybrid) for production
3. **Long-term**: Consider Strategy 5 (Historical) for personalization

Would you like me to implement Strategy 1 (Keyword-Based) first as the MVP solution?
