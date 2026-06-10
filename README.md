# GolPredictor Bot

Automated bot for filling football match predictions on GolPredictor using Selenium and custom prediction models.

## Features

- **Selenium Automation**: Automatically logs in and fills predictions on GolPredictor
- **Prediction Engine**: Extensible framework for various prediction models
- **Configuration Management**: Secure credential handling via `.env` files
- **Logging**: Comprehensive logging for debugging and monitoring

## Project Structure

```
gol-predictor/
├── bot.py              # Selenium automation bot
├── predictor.py        # Prediction engine and models
├── config.py           # Configuration management
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md          # This file
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ildabaoth/gol-predictor.git
cd gol-predictor
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
GOLPREDICTOR_EMAIL=your_email@example.com
GOLPREDICTOR_PASSWORD=your_password
HEADLESS_MODE=True
BROWSER_TIMEOUT=30
```

⚠️ **Never commit `.env` to Git** - it contains sensitive credentials.

## Usage

### Basic Usage

```python
from bot import GolPredictorBot
from predictor import SimplePredictor

bot = GolPredictorBot()
predictor = SimplePredictor()

try:
    bot.run(predictor)
except Exception as e:
    print(f"Error: {e}")
```

### Run from Command Line

```bash
python main.py
```

## Customization

### Creating a Custom Predictor

Extend the `FootballPredictor` class:

```python
from predictor import FootballPredictor

class MyPredictor(FootballPredictor):
    def predict_match(self, home_team: str, away_team: str, **kwargs) -> Dict:
        # Your prediction logic here
        return {
            "home_win": 0.5,
            "draw": 0.3,
            "away_win": 0.2,
            "predicted_winner": "home_win",
            "confidence": 0.5,
            "notes": "Custom prediction"
        }
```

### Integrating External Data

You can fetch team statistics from:
- [API-Football](https://www.api-football.com/)
- [Football-Data.org](https://www.football-data.org/)
- Other sports data APIs

## Important Notes

⚠️ **Terms of Service**: Before using this bot, ensure you comply with GolPredictor's Terms of Service. Automated submissions may be against their policies.

⚠️ **Credentials**: Never share your `.env` file or commit credentials to version control.

⚠️ **Page Structure**: The Selenium selectors (IDs, classes) need to be verified and updated based on the actual GolPredictor page structure. Inspect the website to find correct selectors.

## Troubleshooting

### WebDriver Issues

If Chrome driver fails to load:

```bash
pip install --upgrade webdriver-manager
```

### Login Fails

- Verify credentials in `.env`
- Check if GolPredictor has changed their page structure
- Inspect the page to find correct element IDs

### Predictions Not Filling

The selectors in `bot.py` are placeholders. You need to:

1. Open GolPredictor in a browser
2. Inspect the page (F12)
3. Find the actual CSS classes/IDs for prediction fields
4. Update the selectors in `bot.py`

## Development

### Testing

```bash
python predictor.py  # Test predictor
python main.py       # Test full bot (requires valid credentials)
```

### Logging

Check logs for detailed execution information:

```python
import logging
logging.getLogger("bot").setLevel(logging.DEBUG)
```

## License

MIT

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This tool is for educational purposes. Use responsibly and ensure compliance with GolPredictor's terms of service.
