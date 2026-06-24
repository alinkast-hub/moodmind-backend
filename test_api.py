
import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:5000"

class MoodMindAPITester:
    def __init__(self):
        self.access_token = None
        self.user_id = None

    def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = requests.get(f"{BASE_URL}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        try:
            user_data = {
                "username": "testuser123",
                "email": "test@moodmind.ai",
                "password": "securepassword123",
                "subscription_type": "free"
            }

            response = requests.post(f"{BASE_URL}/register", json=user_data)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                self.access_token = data['access_token']
                self.user_id = data['user']['id']
                print(f"Registration successful! User ID: {self.user_id}")
                print(f"Access token received: {self.access_token[:20]}...")
                return True
            else:
                print(f"Registration failed: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_user_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
        try:
            login_data = {
                "username": "testuser123",
                "password": "securepassword123"
            }

            response = requests.post(f"{BASE_URL}/login", json=login_data)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                print(f"Login successful!")
                print(f"New access token: {self.access_token[:20]}...")
                return True
            else:
                print(f"Login failed: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_create_journal_entry(self):
        """Test creating journal entries"""
        print("\n=== Testing Journal Entry Creation ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        # Test multiple journal entries
        journal_entries = [
            {
                "text": "Today was an amazing day! I got promoted at work and I'm feeling incredibly happy and excited about the future.",
                "mood_score": 9
            },
            {
                "text": "I'm feeling really anxious about the upcoming presentation. My heart is racing and I can't stop worrying about it.",
                "mood_score": 3
            },
            {
                "text": "Had a normal day today. Nothing special happened, just went through my usual routine.",
                "mood_score": 5
            },
            {
                "text": "I'm so frustrated with everything going wrong today. Traffic was terrible, missed my meeting, and now I'm angry.",
                "mood_score": 2
            }
        ]

        success_count = 0
        for i, entry_data in enumerate(journal_entries, 1):
            try:
                print(f"\nCreating journal entry {i}...")
                response = requests.post(f"{BASE_URL}/journal", json=entry_data, headers=headers)
                print(f"Status Code: {response.status_code}")

                if response.status_code == 201:
                    data = response.json()
                    print(f"Entry created successfully!")
                    print(f"Dominant emotion: {data['ai_analysis']['dominant_emotion']}")
                    print(f"AI Response: {data['ai_analysis']['ai_response'][:100]}...")
                    success_count += 1
                else:
                    print(f"Failed to create entry: {response.json()}")

            except Exception as e:
                print(f"Error creating entry {i}: {e}")

        return success_count > 0

    def test_journal_history(self):
        """Test retrieving journal history"""
        print("\n=== Testing Journal History Retrieval ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(f"{BASE_URL}/journal/history", headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Retrieved {len(data['entries'])} journal entries")
                print(f"Pagination info: Page {data['pagination']['page']} of {data['pagination']['pages']}")

                if data['entries']:
                    print(f"\nFirst entry preview:")
                    entry = data['entries'][0]
                    print(f"  Mood Score: {entry['mood_score']}")
                    print(f"  Text: {entry['text'][:50]}...")
                    print(f"  Emotions: {entry['emotions']}")

                return True
            else:
                print(f"Failed to retrieve history: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_text_analysis(self):
        """Test text analysis endpoint"""
        print("\n=== Testing Text Analysis ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            analysis_data = {
                "text": "I'm feeling overwhelmed with work and stressed about deadlines. Everything seems to be piling up.",
                "mood_score": 4
            }

            response = requests.post(f"{BASE_URL}/analyze", json=analysis_data, headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                analysis = data['analysis']
                print(f"Analysis successful!")
                print(f"Dominant emotion: {analysis['dominant_emotion']}")
                print(f"Emotions breakdown: {analysis['emotions']}")
                print(f"AI Response: {analysis['ai_response'][:100]}...")
                return True
            else:
                print(f"Analysis failed: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_mood_statistics(self):
        """Test mood statistics endpoint"""
        print("\n=== Testing Mood Statistics ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(f"{BASE_URL}/mood/stats", headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                stats = data['stats']
                print(f"Statistics retrieved successfully!")
                print(f"Total entries: {stats['total_entries']}")
                print(f"Average mood: {stats['average_mood']}")
                print(f"Weekly average: {stats['weekly_average']}")
                print(f"Mood trend: {stats['mood_trend']}")
                print(f"Burnout warning: {stats['burnout_warning']}")
                print(f"Mood distribution: {stats['mood_distribution']}")
                return True
            else:
                print(f"Failed to get statistics: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_subscription_check(self):
        """Test subscription check endpoint"""
        print("\n=== Testing Subscription Check ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(f"{BASE_URL}/subscription/check", headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Subscription check successful!")
                print(f"Subscription type: {data['subscription_type']}")
                print(f"Daily limit: {data['daily_limit']}")
                print(f"Current usage: {data['current_usage']}")
                print(f"Remaining entries: {data['remaining_entries']}")
                print(f"Is premium: {data['is_premium']}")
                return True
            else:
                print(f"Subscription check failed: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def test_user_profile(self):
        """Test user profile endpoint"""
        print("\n=== Testing User Profile ===")

        if not self.access_token:
            print("No access token available. Please login first.")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                user = data['user']
                print(f"Profile retrieved successfully!")
                print(f"Username: {user['username']}")
                print(f"Email: {user['email']}")
                print(f"Subscription: {user['subscription_type']}")
                print(f"Created: {user['created_at']}")
                return True
            else:
                print(f"Failed to get profile: {response.json()}")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting MoodMind AI API Tests...")
        print("=" * 50)

        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Journal Entry Creation", self.test_create_journal_entry),
            ("Journal History", self.test_journal_history),
            ("Text Analysis", self.test_text_analysis),
            ("Mood Statistics", self.test_mood_statistics),
            ("Subscription Check", self.test_subscription_check),
            ("User Profile", self.test_user_profile)
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"Test {test_name} crashed: {e}")
                results.append((test_name, False))

        # Print summary
        print("\n" + "=" * 50)
        print("🏁 TEST SUMMARY")
        print("=" * 50)

        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1

        print(f"\nTotal: {passed}/{len(results)} tests passed")

        if passed == len(results):
            print("🎉 All tests passed! Your MoodMind AI API is working perfectly!")
        else:
            print("⚠️  Some tests failed. Please check the API implementation.")

if __name__ == "__main__":
    tester = MoodMindAPITester()
    tester.run_all_tests()
