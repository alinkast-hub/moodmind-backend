# MoodMind AI - Flask REST API Backend

A comprehensive Flask REST API backend for the MoodMind AI mental health and mood journal mobile application.

## Features

- **User Authentication**: JWT-based registration and login system
- **Journal Management**: Create and retrieve mood journal entries
- **AI Sentiment Analysis**: Automatic emotion detection and supportive AI responses
- **Mood Statistics**: Track mood trends and burnout warnings
- **Subscription Management**: Free (3 entries/day) and Premium (unlimited) tiers
- **Production Ready**: Comprehensive error handling and validation

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login

### Journal Management
- `POST /journal` - Create a new journal entry
- `GET /journal/history` - Get user's journal history (paginated)

### AI Analysis
- `POST /analyze` - Analyze text for sentiment and emotions

### Statistics & Insights
- `GET /mood/stats` - Get mood statistics and trends
- `GET /subscription/check` - Check subscription status and usage

### User Management
- `GET /user/profile` - Get user profile information
- `GET /health` - Health check endpoint

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # edit .env and set a real JWT_SECRET_KEY
   ```

   `JWT_SECRET_KEY` is required — the app will refuse to start without it.

3. **Run the Application**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

4. **Test the API**
   ```bash
   python test_api.py
   ```

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `subscription_type` ('free' or 'premium')
- `created_at`

### Journal Entries Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `text` (Journal content)
- `mood_score` (1-10 scale)
- `emotions` (JSON string of detected emotions)
- `ai_response` (AI-generated supportive response)
- `created_at`

### Daily Usage Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `date`
- `entry_count`

## AI Features

### Emotion Detection
The AI service detects five primary emotions:
- **Happy**: Joy, excitement, contentment
- **Sad**: Depression, melancholy, disappointment
- **Anxious**: Worry, stress, nervousness
- **Angry**: Frustration, irritation, rage
- **Neutral**: Calm, balanced, ordinary

### Supportive Responses
AI generates personalized supportive responses based on:
- Dominant emotion detected
- Mood score (1-10)
- Mental health best practices
- Wellness tips and recommendations

### Burnout Detection
Automatically detects potential burnout when:
- Mood score < 4 for 3+ consecutive days
- Provides appropriate warnings and suggestions

## Subscription Tiers

### Free Tier
- 3 journal entries per day
- Full AI analysis and responses
- Basic mood statistics

### Premium Tier
- Unlimited journal entries
- Advanced analytics (future feature)
- Priority support (future feature)

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Werkzeug secure password hashing
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Production-ready error responses
- **CORS Support**: Cross-origin resource sharing enabled

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and adjust as needed. `python-dotenv` loads it automatically on startup.

```bash
JWT_SECRET_KEY=your-super-secret-key-here   # required, app will not start without it
DATABASE_URL=sqlite:///moodmind.db          # use a PostgreSQL URL in production
FLASK_DEBUG=False
PORT=5000
```

### Development Configuration
The application uses SQLite by default for development. For production, configure a proper database like PostgreSQL via `DATABASE_URL`.

## API Usage Examples

### Register a New User
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Create a Journal Entry
```bash
curl -X POST http://localhost:5000/journal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "text": "Today was a great day! I feel happy and accomplished.",
    "mood_score": 8
  }'
```

### Get Mood Statistics
```bash
curl -X GET http://localhost:5000/mood/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing

The `test_api.py` script provides comprehensive testing for all endpoints:

```bash
python test_api.py
```

Tests include:
- Health check
- User registration and login
- Journal entry creation
- History retrieval
- AI text analysis
- Mood statistics
- Subscription checking
- User profile management

## File Structure

```
moodmind-backend/
├── app.py              # Main Flask application
├── models.py           # Database models
├── ai_service.py       # AI sentiment analysis service
├── test_api.py         # Comprehensive API tests
├── requirements.txt    # Python dependencies
├── Procfile            # Process definition for Railway/Heroku-style deploys
├── .env.example        # Template for required environment variables
├── README.md           # This documentation
└── moodmind.db         # SQLite database (created automatically, gitignored)
```

## Production Deployment

### Security Checklist
- [ ] Change JWT_SECRET_KEY to a strong, random value
- [ ] Use a production database (PostgreSQL, MySQL)
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Set up monitoring and health checks
- [ ] Use environment variables for sensitive configuration

### Recommended Deployment Platforms
This project ships with a `Procfile` (`gunicorn app:app`) targeting **Railway**, which provisions `DATABASE_URL` and runs the `Procfile` automatically. It also works on any platform that supports `Procfile`-based deploys:
- **Railway**: Push the repo, set `JWT_SECRET_KEY`, attach a PostgreSQL plugin for `DATABASE_URL`
- **Heroku**: Same `Procfile` works, add a PostgreSQL addon
- **AWS / DigitalOcean / Google Cloud**: Run `gunicorn app:app` behind your platform's process manager

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

---

**MoodMind AI** - Empowering mental health through AI-driven insights and supportive technology.
