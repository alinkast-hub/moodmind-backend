from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta, date
from models import db, User, JournalEntry, DailyUsage
from ai_service import AIService
import os

app = Flask(__name__)

# Configuration for Railway
jwt_secret = os.environ.get('JWT_SECRET_KEY')
if not jwt_secret:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required")
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

database_url = os.environ.get('DATABASE_URL', 'sqlite:///moodmind.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
jwt = JWTManager(app)
CORS(app)
db.init_app(app)

# Initialize AI service
ai_service = AIService()

# Create tables
with app.app_context():
    db.create_all()

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

# Helper function to check subscription limits
def check_subscription_limit(user_id):
    """Check if user has reached daily entry limit"""
    user = User.query.get(user_id)
    if user.subscription_type == 'premium':
        return True, 0  # Unlimited for premium users

    # Check daily usage for free users
    today = date.today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()

    if not usage:
        # Create new usage record
        usage = DailyUsage(user_id=user_id, date=today, entry_count=0)
        db.session.add(usage)
        db.session.commit()

    return usage.entry_count < 3, usage.entry_count

def increment_daily_usage(user_id):
    """Increment daily usage count"""
    today = date.today()
    usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()

    if usage:
        usage.entry_count += 1
    else:
        usage = DailyUsage(user_id=user_id, date=today, entry_count=1)
        db.session.add(usage)

    db.session.commit()

# Routes
@app.route('/', methods=['GET'])
def home():
    """Home endpoint - ВИПРАВЛЕННЯ 404 ПОМИЛКИ"""
    return jsonify({
        'message': 'MoodMind AI Backend API',
        'version': '1.0.0',
        'status': 'running',
        'description': 'AI-powered mental health and mood journal backend',
        'endpoints': {
            'health': '/health',
            'register': '/register',
            'login': '/login',
            'journal': '/journal',
            'journal_history': '/journal/history',
            'analyze': '/analyze',
            'mood_stats': '/mood/stats',
            'subscription_check': '/subscription/check',
            'user_profile': '/user/profile'
        },
        'documentation': 'https://github.com/alinkast-hub/moodmind-backend'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400

        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            subscription_type=data.get('subscription_type', 'free')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token (identity must be a string for flask-jwt-extended 4.x)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Missing username or password'}), 400

        # Find user
        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create access token (identity must be a string for flask-jwt-extended 4.x)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500

@app.route('/journal', methods=['POST'])
@jwt_required()
def create_journal_entry():
    """Create a new journal entry"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not all(k in data for k in ('text', 'mood_score')):
            return jsonify({'error': 'Missing required fields: text, mood_score'}), 400

        # Validate mood score
        mood_score = data['mood_score']
        if not isinstance(mood_score, int) or mood_score < 1 or mood_score > 10:
            return jsonify({'error': 'Mood score must be an integer between 1 and 10'}), 400

        # Check subscription limits
        can_create, current_count = check_subscription_limit(user_id)
        if not can_create:
            return jsonify({
                'error': 'Daily limit reached',
                'message': 'Free users can create up to 3 entries per day. Upgrade to premium for unlimited entries.',
                'current_count': current_count,
                'limit': 3
            }), 403

        # Analyze journal entry with AI
        ai_analysis = ai_service.analyze_journal_entry(data['text'], mood_score)

        # Create journal entry
        entry = JournalEntry(
            user_id=user_id,
            text=data['text'],
            mood_score=mood_score,
            ai_response=ai_analysis['ai_response']
        )
        entry.set_emotions(ai_analysis['emotions'])

        db.session.add(entry)

        # Increment daily usage
        increment_daily_usage(user_id)

        db.session.commit()

        return jsonify({
            'message': 'Journal entry created successfully',
            'entry': entry.to_dict(),
            'ai_analysis': {
                'emotions': ai_analysis['emotions'],
                'dominant_emotion': ai_analysis['dominant_emotion'],
                'ai_response': ai_analysis['ai_response']
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create journal entry', 'message': str(e)}), 500

@app.route('/journal/history', methods=['GET'])
@jwt_required()
def get_journal_history():
    """Get user's journal entry history"""
    try:
        user_id = int(get_jwt_identity())

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Limit per_page to prevent abuse
        per_page = min(per_page, 50)

        # Get entries with pagination
        entries = JournalEntry.query.filter_by(user_id=user_id)\
                                  .order_by(JournalEntry.created_at.desc())\
                                  .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'entries': [entry.to_dict() for entry in entries.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': entries.total,
                'pages': entries.pages,
                'has_next': entries.has_next,
                'has_prev': entries.has_prev
            }
        })

    except Exception as e:
        return jsonify({'error': 'Failed to retrieve journal history', 'message': str(e)}), 500

@app.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_text():
    """Analyze text for sentiment and emotions"""
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400

        mood_score = data.get('mood_score', 5)  # Default to neutral

        # Perform AI analysis
        analysis = ai_service.analyze_journal_entry(data['text'], mood_score)

        return jsonify({
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500

@app.route('/mood/stats', methods=['GET'])
@jwt_required()
def get_mood_stats():
    """Get mood statistics and trends"""
    try:
        user_id = int(get_jwt_identity())

        # Get date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get entries in date range
        entries = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= start_date,
            JournalEntry.created_at <= end_date
        ).order_by(JournalEntry.created_at.desc()).all()

        if not entries:
            return jsonify({
                'message': 'No entries found in the specified date range',
                'stats': {
                    'total_entries': 0,
                    'average_mood': 0,
                    'mood_trend': 'neutral',
                    'burnout_warning': False
                }
            })

        # Calculate statistics
        mood_scores = [entry.mood_score for entry in entries]
        total_entries = len(entries)
        average_mood = sum(mood_scores) / total_entries

        # Calculate weekly average for trend
        weekly_entries = [entry for entry in entries if entry.created_at >= (end_date - timedelta(days=7))]
        weekly_average = sum(entry.mood_score for entry in weekly_entries) / len(weekly_entries) if weekly_entries else average_mood

        # Determine trend
        if weekly_average > average_mood + 0.5:
            trend = 'improving'
        elif weekly_average < average_mood - 0.5:
            trend = 'declining'
        else:
            trend = 'stable'

        # Check for burnout warning (mood < 4 for 3+ consecutive days)
        burnout_warning = False
        consecutive_low_days = 0

        # Group entries by date
        daily_moods = {}
        for entry in entries:
            entry_date = entry.created_at.date()
            if entry_date not in daily_moods:
                daily_moods[entry_date] = []
            daily_moods[entry_date].append(entry.mood_score)

        # Calculate daily averages and check for consecutive low days
        sorted_dates = sorted(daily_moods.keys(), reverse=True)
        for entry_date in sorted_dates:
            daily_average = sum(daily_moods[entry_date]) / len(daily_moods[entry_date])
            if daily_average < 4:
                consecutive_low_days += 1
                if consecutive_low_days >= 3:
                    burnout_warning = True
                    break
            else:
                consecutive_low_days = 0

        # Mood distribution
        mood_distribution = {
            'very_low': len([m for m in mood_scores if m <= 2]),
            'low': len([m for m in mood_scores if 3 <= m <= 4]),
            'neutral': len([m for m in mood_scores if 5 <= m <= 6]),
            'good': len([m for m in mood_scores if 7 <= m <= 8]),
            'excellent': len([m for m in mood_scores if m >= 9])
        }

        return jsonify({
            'stats': {
                'total_entries': total_entries,
                'average_mood': round(average_mood, 2),
                'weekly_average': round(weekly_average, 2),
                'mood_trend': trend,
                'burnout_warning': burnout_warning,
                'consecutive_low_days': consecutive_low_days,
                'mood_distribution': mood_distribution,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        })

    except Exception as e:
        return jsonify({'error': 'Failed to calculate mood statistics', 'message': str(e)}), 500

@app.route('/subscription/check', methods=['GET'])
@jwt_required()
def check_subscription():
    """Check user's subscription status and usage"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get today's usage
        today = date.today()
        usage = DailyUsage.query.filter_by(user_id=user_id, date=today).first()
        current_usage = usage.entry_count if usage else 0

        # Calculate limits based on subscription
        if user.subscription_type == 'premium':
            daily_limit = None  # Unlimited
            remaining = None
        else:
            daily_limit = 3
            remaining = max(0, daily_limit - current_usage)

        return jsonify({
            'subscription_type': user.subscription_type,
            'daily_limit': daily_limit,
            'current_usage': current_usage,
            'remaining_entries': remaining,
            'is_premium': user.subscription_type == 'premium'
        })

    except Exception as e:
        return jsonify({'error': 'Failed to check subscription', 'message': str(e)}), 500

@app.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user profile information"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()})

    except Exception as e:
        return jsonify({'error': 'Failed to get user profile', 'message': str(e)}), 500

if __name__ == '__main__':
    # RAILWAY PRODUCTION
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
