
from textblob import TextBlob
import re
import random

class AIService:
    def __init__(self):
        # Emotion keywords mapping
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'pleased', 'content', 'glad', 'elated', 'thrilled'],
            'sad': ['sad', 'depressed', 'down', 'blue', 'melancholy', 'sorrowful', 'grief', 'heartbroken', 'disappointed', 'dejected'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'panic', 'fear', 'concerned', 'uneasy', 'tense', 'restless'],
            'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage', 'frustrated', 'outraged', 'livid', 'hostile'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'regular', 'typical', 'ordinary', 'standard', 'usual', 'calm']
        }

        # Supportive responses based on emotions
        self.supportive_responses = {
            'happy': [
                "It's wonderful to see you feeling so positive! Keep embracing these joyful moments.",
                "Your happiness is contagious! Remember to savor these beautiful feelings.",
                "I'm so glad you're experiencing joy. These moments are precious - hold onto them!",
                "Your positive energy shines through! Keep nurturing what brings you happiness."
            ],
            'sad': [
                "I hear that you're going through a difficult time. Remember, it's okay to feel sad - these emotions are valid.",
                "Your feelings matter, and it's brave of you to acknowledge them. Take things one day at a time.",
                "Sadness can be overwhelming, but you're not alone. Consider reaching out to someone you trust.",
                "It's natural to feel down sometimes. Be gentle with yourself and remember that this feeling will pass."
            ],
            'anxious': [
                "Anxiety can feel overwhelming, but you're taking a positive step by expressing these feelings.",
                "Try some deep breathing exercises. Remember, you've overcome challenges before and you can do it again.",
                "It's okay to feel anxious. Consider breaking down your worries into smaller, manageable pieces.",
                "Your anxiety is valid. Focus on what you can control and be kind to yourself during this time."
            ],
            'angry': [
                "It sounds like you're dealing with some frustrating situations. Your anger is a valid emotion.",
                "When we feel angry, it often signals that something important to us needs attention. Take time to process these feelings.",
                "Anger can be intense. Consider healthy ways to express and release these emotions, like physical activity or journaling.",
                "It's okay to feel angry. Try to identify what's behind this emotion and address it constructively."
            ],
            'neutral': [
                "It's perfectly fine to feel neutral or calm. Sometimes steady emotions are exactly what we need.",
                "Neutral feelings can be a sign of balance and stability. How are you taking care of yourself today?",
                "It sounds like you're in a peaceful state. This can be a good time for reflection and self-care.",
                "Feeling okay is completely valid. Remember to check in with yourself regularly."
            ]
        }

    def analyze_sentiment(self, text):
        """
        Analyze sentiment and detect emotions from journal text
        Returns: dict with emotions and confidence scores
        """
        # Clean and normalize text
        text_lower = text.lower()

        # Use TextBlob for basic sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1

        # Detect emotions based on keywords
        emotions = {
            'happy': 0,
            'sad': 0,
            'anxious': 0,
            'angry': 0,
            'neutral': 0
        }

        # Count emotion keywords
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotions[emotion] += 1

        # Adjust based on TextBlob polarity
        if polarity > 0.3:
            emotions['happy'] += 2
        elif polarity < -0.3:
            emotions['sad'] += 2
        elif abs(polarity) <= 0.1:
            emotions['neutral'] += 1

        # Normalize emotions to percentages
        total_score = sum(emotions.values())
        if total_score > 0:
            for emotion in emotions:
                emotions[emotion] = round((emotions[emotion] / total_score) * 100, 1)
        else:
            # Default to neutral if no emotions detected
            emotions['neutral'] = 100.0

        return {
            'emotions': emotions,
            'polarity': round(polarity, 2),
            'subjectivity': round(subjectivity, 2),
            'dominant_emotion': max(emotions, key=emotions.get)
        }

    def generate_supportive_response(self, emotions_analysis, mood_score):
        """
        Generate AI supportive response based on emotion analysis and mood score
        """
        dominant_emotion = emotions_analysis['dominant_emotion']

        # Select base response based on dominant emotion
        base_responses = self.supportive_responses.get(dominant_emotion, self.supportive_responses['neutral'])
        response = random.choice(base_responses)

        # Add mood-specific guidance
        if mood_score <= 3:
            response += " If you're consistently feeling low, please consider reaching out to a mental health professional or trusted friend."
        elif mood_score <= 5:
            response += " Remember to practice self-care and engage in activities that usually bring you comfort."
        elif mood_score >= 8:
            response += " It's great to see you in such a positive space! Consider what contributed to this feeling."

        # Add general wellness tip
        wellness_tips = [
            " Remember to stay hydrated and get enough rest.",
            " Consider taking a few minutes for mindfulness or meditation.",
            " Physical activity, even a short walk, can be beneficial for your mood.",
            " Connecting with loved ones can provide valuable support.",
            " Journaling regularly can help you track patterns and progress."
        ]

        response += random.choice(wellness_tips)

        return response

    def analyze_journal_entry(self, text, mood_score):
        """
        Complete analysis of journal entry
        Returns: dict with emotions and AI response
        """
        emotions_analysis = self.analyze_sentiment(text)
        ai_response = self.generate_supportive_response(emotions_analysis, mood_score)

        return {
            'emotions': emotions_analysis['emotions'],
            'dominant_emotion': emotions_analysis['dominant_emotion'],
            'sentiment_polarity': emotions_analysis['polarity'],
            'ai_response': ai_response
        }
