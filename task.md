# AI Scoring System - Task Documentation

## Overview
This document outlines the approach for developing an AI-powered scoring system that evaluates LinkedIn users based on how their activities align with your intent/goals.

## Core Concept
Score users (0-100) based on semantic similarity between their LinkedIn activities (posts, comments, reactions, profile) and your defined intent using AI embeddings.

---

## 1. Intent Definition

### Intent Components
Your intent can be defined using:

1. **Keywords**: List of relevant keywords/topics
   - Example: `["AI", "machine learning", "startups", "technology", "innovation"]`

2. **Description**: Natural language description
   - Example: `"Looking for users interested in AI and tech innovation"`

3. **Activity Weights**: Importance weights for different activity types
   - Posts: 40%
   - Comments: 30%
   - Reactions: 20%
   - Profile: 10%

### Intent Configuration Structure
```python
{
    "keywords": ["keyword1", "keyword2", ...],
    "description": "Your intent description",
    "weights": {
        "posts": 0.4,
        "comments": 0.3,
        "reactions": 0.2,
        "profile": 0.1
    }
}
```

---

## 2. Data Structure Understanding

### Activity Types in LinkedIn Data

#### A. Posts (Updates)
- **Location**: `Update.commentary.text`
- **Structure**: `Update` object with `commentary` field containing post content
- **Identification**: Update with `commentary.text` and no reaction header
- **Source**: `posts.json` → `feedDashProfileUpdatesByMemberShareFeed`

#### B. Comments
- **Location**: `Update.highlighted_comments` → `Comment.commentary.text`
- **Structure**: 
  - Comments are nested under posts via `Update.highlighted_comments`
  - Each `Comment` can have nested `replies` (recursive structure)
- **Identification**: Extract from `Update.highlighted_comments` list
- **Source**: `comment.json` → Contains Updates where user commented

#### C. Reactions
- **Location**: `Update.header.text` (reaction type) + `Update.commentary.text` (content reacted to)
- **Types**:
  - Like: `header.text` contains "liked"
  - Love: `header.text` contains "loves"
  - Insightful: `header.text` contains "insightful"
  - Comment: `header.text` contains "commented" (this is also a comment activity)
- **Target Identification**:
  - Reaction on Post: `Update.commentary.text` is long (>200 chars typically)
  - Reaction on Comment: `Update.commentary.text` is short (<200 chars typically)
- **Source**: `reaction.json` → `feedDashProfileUpdatesByMemberReactions`

#### D. Profile Information
- **Location**: `ActorComponent` fields
- **Fields**:
  - `name.text`: User's name
  - `description.text`: User's headline/description
  - `sub_description.text`: Additional profile info
- **Source**: Available in all Update objects via `Update.actor`

---

## 3. Activity Extraction Strategy

### 3.1 Post Extraction
```python
def extract_posts(update: Update) -> str:
    """
    Extract post content from Update.
    Post: Update with commentary and no reaction header.
    """
    if update.commentary and update.commentary.text:
        # Check if it's a post (not a reaction)
        if not update.header or "liked" not in update.header.text.lower():
            return update.commentary.text
    return None
```

### 3.2 Comment Extraction (Including Nested Replies)
```python
def extract_all_comments(update: Update) -> List[str]:
    """
    Extract all comments from a post, including nested replies.
    Recursively extracts from Update.highlighted_comments.
    """
    comments = []
    
    def extract_recursive(comment: Comment):
        if comment.commentary and comment.commentary.text:
            comments.append(comment.commentary.text)
        # Recursively extract replies
        for reply in comment.replies:
            extract_recursive(reply)
    
    # Extract from highlighted comments
    for comment in update.highlighted_comments:
        extract_recursive(comment)
    
    return comments
```

### 3.3 Reaction Classification and Extraction
```python
def classify_and_extract_reaction(update: Update) -> dict:
    """
    Classify reaction type and extract content.
    Returns: {
        "type": "comment_reaction" | "reaction_on_post" | "reaction_on_comment",
        "content": str,
        "reaction_type": "like" | "love" | "insightful" | "comment"
    }
    """
    header_text = update.header.text.lower() if update.header else ""
    commentary_text = update.commentary.text if update.commentary else ""
    
    # Check if user commented (this is a comment activity)
    if "commented" in header_text:
        return {
            "type": "comment_reaction",
            "content": commentary_text,
            "reaction_type": "comment"
        }
    
    # Check for other reaction types
    elif any(word in header_text for word in ["liked", "loves", "insightful"]):
        # Determine if reaction is on post or comment
        if len(commentary_text) > 200:  # Heuristic: posts are typically longer
            return {
                "type": "reaction_on_post",
                "content": commentary_text,
                "reaction_type": "like" if "liked" in header_text else 
                               "love" if "loves" in header_text else "insightful"
            }
        else:
            return {
                "type": "reaction_on_comment",
                "content": commentary_text,
                "reaction_type": "like" if "liked" in header_text else 
                               "love" if "loves" in header_text else "insightful"
            }
    
    return None
```

### 3.4 Profile Extraction
```python
def extract_profile(actor: ActorComponent) -> str:
    """
    Extract profile information from ActorComponent.
    Combines name, description, and sub_description.
    """
    profile_parts = []
    
    if actor.name and actor.name.text:
        profile_parts.append(actor.name.text)
    if actor.description and actor.description.text:
        profile_parts.append(actor.description.text)
    if actor.sub_description and actor.sub_description.text:
        profile_parts.append(actor.sub_description.text)
    
    return " ".join(profile_parts)
```

---

## 4. AI Scoring Methodology

### 4.1 Semantic Similarity Using Embeddings

**Technology**: Sentence Transformers (e.g., `all-MiniLM-L6-v2`)
- Converts text to high-dimensional vectors (embeddings)
- Computes cosine similarity between activity text and intent
- Score range: 0.0 (no match) to 1.0 (perfect match)

### 4.2 Scoring Process

1. **Create Intent Embedding**:
   - Combine keywords and description into single text
   - Generate embedding vector for intent

2. **Create Activity Embeddings**:
   - For each activity (post, comment, reaction, profile), generate embedding

3. **Compute Similarity**:
   - Cosine similarity between activity embedding and intent embedding
   - Formula: `similarity = cosine(activity_embedding, intent_embedding)`

4. **Normalize to 0-100 Scale**:
   - Multiply similarity score by 100

---

## 5. Scoring Formula

### 5.1 Component Scores

For each user, calculate:

#### A. Post Score
```
Post Score = Average similarity of all user's posts
```
- Extract all posts from user's activity
- Score each post against intent
- Average all post scores

#### B. Comment Score
```
Comment Score = Average similarity of all user's comments (including replies)
```
- Extract all comments (including nested replies) from all posts
- Score each comment against intent
- Average all comment scores

#### C. Reaction Score
```
Reaction Score = Weighted average of reactions:
  - Reactions on Posts: Score(post_content) × 0.6
  - Reactions on Comments: Score(comment_content) × 0.4
  - Comment-type reactions: Score as comments (included in Comment Score)
```
- Classify each reaction (on post vs on comment)
- Score the content being reacted to
- Apply weights based on reaction type

#### D. Profile Score
```
Profile Score = Similarity of user's profile (name + description + sub_description)
```
- Combine all profile fields into single text
- Score against intent

### 5.2 Final User Score

```
Final Score = (Post Score × 0.4) + 
              (Comment Score × 0.3) + 
              (Reaction Score × 0.2) + 
              (Profile Score × 0.1)
```

**Score Range**: 0-100
- 0-30: Low alignment
- 30-60: Moderate alignment
- 60-80: Good alignment
- 80-100: Excellent alignment

---

## 6. Implementation Architecture

### 6.1 File Structure
```
scoring/
├── __init__.py
├── intent.py          # Intent configuration model
├── scorer.py          # AI scoring engine (embeddings + similarity)
├── user_activity.py   # Activity extraction from data models
└── user_score.py      # User score models and aggregation

score_users.py         # Main script to run scoring
```

### 6.2 Key Classes

#### IntentConfig
```python
@dataclass
class IntentConfig:
    keywords: List[str]
    description: str
    weights: Dict[str, float]  # {"posts": 0.4, "comments": 0.3, ...}
```

#### ActivityExtractor
```python
class ActivityExtractor:
    def extract_posts(self, updates: List[Update]) -> Dict[str, List[str]]
    def extract_comments(self, updates: List[Update]) -> Dict[str, List[str]]
    def extract_reactions(self, updates: List[Update]) -> Dict[str, List[dict]]
    def extract_profiles(self, updates: List[Update]) -> Dict[str, str]
```

#### AIScorer
```python
class AIScorer:
    def __init__(self, intent: IntentConfig)
    def score_text(self, text: str) -> float
    def score_user(self, activities: UserActivities) -> UserScore
```

#### UserScore
```python
@dataclass
class UserScore:
    user_id: str
    user_name: str
    final_score: float
    post_score: float
    comment_score: float
    reaction_score: float
    profile_score: float
    activity_counts: Dict[str, int]
```

---

## 7. Data Flow

```
1. Load LinkedIn Data
   ├── posts.json → Parse posts
   ├── comment.json → Parse comments
   └── reaction.json → Parse reactions

2. Extract Activities by User
   ├── Group updates by actor (user)
   ├── Extract posts per user
   ├── Extract comments per user
   ├── Extract reactions per user
   └── Extract profiles per user

3. Score Activities
   ├── Create intent embedding
   ├── For each user:
   │   ├── Score all posts → Post Score
   │   ├── Score all comments → Comment Score
   │   ├── Score all reactions → Reaction Score
   │   └── Score profile → Profile Score

4. Aggregate Scores
   ├── Calculate weighted final score per user
   └── Rank users by final score

5. Output Results
   ├── Top N users with scores
   ├── Score breakdown per user
   └── Activity statistics
```

---

## 8. Key Considerations

### 8.1 Comment Independence
- **Important**: Comments should be scored independently from posts
- A user's comment may align with your intent even if the post doesn't
- Comments show active engagement and specific interest

### 8.2 Reaction Context
- Reactions on posts vs comments should be weighted differently
- Comment-type reactions (user wrote something) are more valuable than passive likes
- Consider reaction type (like, love, insightful) for weighting

### 8.3 Activity Volume
- Users with more activities have more data points
- Consider activity count in scoring (more activities = more reliable score)
- Handle edge cases: users with no posts, only comments, etc.

### 8.4 Recursive Comment Extraction
- Comments can have nested replies (Comment.replies)
- Must recursively extract all levels of replies
- Each reply is scored independently

### 8.5 Reaction Target Identification
- Use heuristics to identify if reaction is on post or comment:
  - Length of commentary text (posts typically longer)
  - Structure analysis
  - Context from header text

---

## 9. Future Enhancements

### 9.1 Advanced Features
- [ ] Time-based weighting (recent activities weighted higher)
- [ ] Engagement quality (comments with replies get higher weight)
- [ ] Multi-intent support (score against multiple intents)
- [ ] Custom weights per user segment
- [ ] Sentiment analysis integration
- [ ] Topic modeling for intent refinement

### 9.2 Performance Optimizations
- [ ] Batch embedding generation
- [ ] Caching of embeddings
- [ ] Parallel processing for multiple users
- [ ] Incremental scoring (update scores as new data arrives)

### 9.3 Output Enhancements
- [ ] Detailed score breakdown visualization
- [ ] Top matching activities per user
- [ ] Intent alignment insights
- [ ] Export to CSV/JSON
- [ ] Dashboard integration

---

## 10. Example Usage

```python
# Define intent
intent = IntentConfig(
    keywords=["AI", "machine learning", "startups"],
    description="Looking for users interested in AI and tech innovation",
    weights={"posts": 0.4, "comments": 0.3, "reactions": 0.2, "profile": 0.1}
)

# Load data
posts_parser = LinkedInDataParser.from_file("posts.json")
comments_parser = LinkedInDataParser.from_file("comment.json")
reactions_parser = LinkedInDataParser.from_file("reaction.json")

# Extract activities
extractor = ActivityExtractor()
all_updates = posts_parser.parse_posts().updates + \
              comments_parser.parse_comments().updates + \
              reactions_parser.parse_reactions().updates

user_activities = extractor.extract_by_user(all_updates)

# Score users
scorer = AIScorer(intent)
user_scores = scorer.score_all_users(user_activities)

# Rank and display
ranked_users = sorted(user_scores, key=lambda x: x.final_score, reverse=True)
for user in ranked_users[:10]:
    print(f"{user.user_name}: {user.final_score:.2f}")
    print(f"  Posts: {user.post_score:.2f}, Comments: {user.comment_score:.2f}")
```

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test activity extraction (posts, comments, reactions)
- Test reaction classification
- Test recursive comment extraction
- Test scoring calculations

### 11.2 Integration Tests
- Test end-to-end scoring pipeline
- Test with real LinkedIn data
- Test edge cases (no activities, single activity type, etc.)

### 11.3 Validation
- Manual review of top-scored users
- Verify intent alignment
- Check score distribution
- Validate activity counts

---

## 12. Dependencies

### Required Packages
```
sentence-transformers>=2.2.0  # For embeddings
numpy>=1.21.0                  # For similarity calculations
scikit-learn>=1.0.0            # For cosine similarity
```

### Optional Packages
```
pandas>=1.3.0                  # For data manipulation
matplotlib>=3.5.0              # For visualizations
```

---

## Notes
- This scoring system uses semantic similarity, not keyword matching
- Scores are relative (0-100 scale) and should be interpreted in context
- Intent definition is crucial - refine keywords and description for better results
- Consider domain-specific embeddings for better accuracy in specialized fields

---

**Last Updated**: 2026-01-24
**Status**: Design Phase - Ready for Implementation
