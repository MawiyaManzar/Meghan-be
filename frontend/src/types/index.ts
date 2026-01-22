// Core types for the Meghan application

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  age_range: AgeRange;
  life_stage: LifeStage;
  primary_struggles: Struggle[];
  privacy_settings: PrivacySettings;
  hearts_balance: number;
  created_at: string;
  updated_at: string;
}

export type AgeRange = '18-20' | '21-23' | '24-25';
export type LifeStage = 'high_school' | 'college' | 'early_career' | 'transition';
export type Struggle = 'anxiety' | 'depression' | 'stress' | 'relationships' | 'career' | 'family' | 'studies';

export interface PrivacySettings {
  anonymity_level: 'full' | 'partial' | 'identified';
  data_sharing: boolean;
  community_visibility: 'public' | 'limited' | 'private';
}

export type ChatMode = 'talk' | 'plan' | 'calm' | 'reflect';

export interface ChatSession {
  id: string;
  user_id: string;
  mode: ChatMode;
  started_at: string;
  ended_at?: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  emotional_tone?: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface Community {
  id: string;
  type: CommunityType;
  name: string;
  description: string;
  member_count: number;
}

export type CommunityType = 'career' | 'relationships' | 'family' | 'studies';

export interface Post {
  id: string;
  author_id: string;
  community_id: string;
  content: string;
  timestamp: string;
  reactions: Reaction[];
  moderation_status: 'approved' | 'flagged' | 'rejected';
}

export interface Reaction {
  id: string;
  user_id: string;
  type: 'heart' | 'support' | 'understanding';
  timestamp: string;
}

export interface WellbeingInsights {
  week_starting: string;
  mood_trends: MoodTrend[];
  trigger_patterns: TriggerPattern[];
  positive_progress: ProgressIndicator[];
  recommendations: Recommendation[];
  encouragement_message: string;
}

export interface MoodTrend {
  date: string;
  mood: number; // 1-10 scale
  energy: number; // 1-10 scale
  anxiety: number; // 1-10 scale
}

export interface TriggerPattern {
  trigger: string;
  frequency: number;
  impact_level: 'low' | 'medium' | 'high';
}

export interface ProgressIndicator {
  area: string;
  improvement: number; // percentage
  description: string;
}

export interface Recommendation {
  type: 'activity' | 'resource' | 'technique';
  title: string;
  description: string;
  hearts_reward?: number;
}