"""LLM-based prediction engine using Google Generative AI (Gemini)"""
import google.generativeai as genai
import logging
from typing import Dict, List
from config import GOOGLE_GENERATIVE_AI_KEY

logger = logging.getLogger(__name__)


class FootballPredictor:
    """
    Base class for football match prediction.
    
    This can be extended with various prediction models:
    - LLM-based prediction (Gemini)
    - Poisson regression
    - Machine learning models
    - Statistical analysis
    - Elo ratings
    """
    
    def __init__(self):
        """Initialize the predictor"""
        pass
    
    def predict_match(self, home_team: str, away_team: str, **kwargs) -> Dict:
        """
        Predict the outcome of a match.
        
        Args:
            home_team: Name of the home team
            away_team: Name of the away team
            **kwargs: Additional parameters (team stats, historical data, etc.)
        
        Returns:
            Dictionary with prediction results:
            {
                "home_team": str,
                "away_team": str,
                "probabilities": {
                    "home_win": float (0-1),
                    "draw": float (0-1),
                    "away_win": float (0-1)
                },
                "predicted_winner": str,
                "confidence": float,
                "reasoning": str,
                "notes": str
            }
        """
        raise NotImplementedError("Subclasses must implement predict_match()")
    
    def predict_multiple(self, matches: List[Dict]) -> List[Dict]:
        """
        Predict outcomes for multiple matches.
        
        Args:
            matches: List of match dictionaries with 'home' and 'away' keys
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        for match in matches:
            try:
                prediction = self.predict_match(
                    home_team=match.get("home"),
                    away_team=match.get("away"),
                    **{k: v for k, v in match.items() if k not in ["home", "away"]}
                )
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting match {match.get('home')} vs {match.get('away')}: {str(e)}")
                continue
        return predictions


class GeminiPredictor(FootballPredictor):
    """
    LLM-based predictor using Google Generative AI (Gemini).
    
    Uses Gemini to analyze match context and generate predictions based on:
    - Team form and history
    - Head-to-head records
    - Player availability
    - Tournament context
    - Other relevant factors
    """
    
    def __init__(self, model_name: str = "gemini-pro"):
        """
        Initialize the Gemini predictor.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        super().__init__()
        genai.configure(api_key=GOOGLE_GENERATIVE_AI_KEY)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Gemini predictor initialized with model: {model_name}")
    
    def _build_prediction_prompt(self, home_team: str, away_team: str, **context) -> str:
        """Build a detailed prompt for Gemini to predict match outcome."""
        
        prompt = f"""You are an expert football (soccer) analyst and predictor. Analyze the following match and provide a prediction.

MATCH DETAILS:
- Home Team: {home_team}
- Away Team: {away_team}

Additional Context:
{self._format_context(context)}

Please analyze this match and provide:
1. Win probability for home team (0-100%)
2. Win probability for away team (0-100%)
3. Draw probability (0-100%)
4. Your predicted winner (home_win, away_win, or draw)
5. Confidence level (0-100%)
6. Brief reasoning (2-3 sentences)

Format your response EXACTLY as follows:
HOME_WIN: <percentage>
AWAY_WIN: <percentage>
DRAW: <percentage>
PREDICTED_WINNER: <home_win|away_win|draw>
CONFIDENCE: <percentage>
REASONING: <your brief reasoning>

Be concise and analytical. Consider current form, historical performance, team strength, and any other relevant factors."""
        
        return prompt
    
    def _format_context(self, context: Dict) -> str:
        """Format additional context for the prompt."""
        if not context:
            return "- No additional context provided"
        
        lines = []
        for key, value in context.items():
            if key not in ["home", "away", "element"]:
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines) if lines else "- No additional context provided"
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini's response into structured prediction data."""
        
        lines = response_text.strip().split("\n")
        prediction = {
            "home_win": 0.33,
            "draw": 0.33,
            "away_win": 0.34,
            "predicted_winner": "draw",
            "confidence": 0.33,
            "reasoning": "Unable to parse response"
        }
        
        try:
            for line in lines:
                if "HOME_WIN:" in line:
                    prediction["home_win"] = float(line.split(":")[-1].strip().replace("%", "")) / 100
                elif "AWAY_WIN:" in line:
                    prediction["away_win"] = float(line.split(":")[-1].strip().replace("%", "")) / 100
                elif "DRAW:" in line:
                    prediction["draw"] = float(line.split(":")[-1].strip().replace("%", "")) / 100
                elif "PREDICTED_WINNER:" in line:
                    winner = line.split(":")[-1].strip().lower()
                    if "home" in winner:
                        prediction["predicted_winner"] = "home_win"
                    elif "away" in winner:
                        prediction["predicted_winner"] = "away_win"
                    else:
                        prediction["predicted_winner"] = "draw"
                elif "CONFIDENCE:" in line:
                    prediction["confidence"] = float(line.split(":")[-1].strip().replace("%", "")) / 100
                elif "REASONING:" in line:
                    prediction["reasoning"] = line.split(":", 1)[-1].strip()
            
            # Normalize probabilities to sum to 1
            total = prediction["home_win"] + prediction["draw"] + prediction["away_win"]
            if total > 0:
                prediction["home_win"] /= total
                prediction["draw"] /= total
                prediction["away_win"] /= total
            
            logger.debug(f"Parsed prediction: {prediction}")
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
        
        return prediction
    
    def predict_match(self, home_team: str, away_team: str, **kwargs) -> Dict:
        """
        Predict match outcome using Gemini LLM.
        
        Args:
            home_team: Name of the home team
            away_team: Name of the away team
            **kwargs: Additional context (team stats, form, etc.)
        
        Returns:
            Dictionary with prediction results
        """
        try:
            logger.info(f"Predicting match: {home_team} vs {away_team}")
            
            # Build prompt
            prompt = self._build_prediction_prompt(home_team, away_team, **kwargs)
            
            # Get Gemini response
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            logger.debug(f"Gemini response: {response_text}")
            
            # Parse response
            prediction_data = self._parse_gemini_response(response_text)
            
            # Build final prediction dictionary
            prediction = {
                "home_team": home_team,
                "away_team": away_team,
                "probabilities": {
                    "home_win": prediction_data["home_win"],
                    "draw": prediction_data["draw"],
                    "away_win": prediction_data["away_win"]
                },
                "predicted_winner": prediction_data["predicted_winner"],
                "confidence": prediction_data["confidence"],
                "reasoning": prediction_data["reasoning"],
                "notes": "Prediction generated by Gemini LLM"
            }
            
            logger.info(f"Prediction complete: {home_team} ({prediction_data['home_win']:.1%}) vs {away_team} ({prediction_data['away_win']:.1%})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting match {home_team} vs {away_team}: {str(e)}")
            # Return neutral prediction on error
            return {
                "home_team": home_team,
                "away_team": away_team,
                "probabilities": {
                    "home_win": 0.33,
                    "draw": 0.34,
                    "away_win": 0.33
                },
                "predicted_winner": "draw",
                "confidence": 0.33,
                "reasoning": f"Error occurred: {str(e)}",
                "notes": "Failed to generate prediction - returning neutral forecast"
            }


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    predictor = GeminiPredictor()
    
    # Test single prediction
    result = predictor.predict_match(
        "Argentina",
        "France",
        tournament="World Cup 2026 Final",
        recent_form="Both teams in excellent form"
    )
    print(f"\nPrediction: {result}")
    
    # Test multiple predictions
    matches = [
        {"home": "Brazil", "away": "Germany", "tournament": "World Cup 2026"},
        {"home": "Spain", "away": "Italy", "tournament": "World Cup 2026"},
    ]
    results = predictor.predict_multiple(matches)
    for r in results:
        print(f"\n{r['home_team']} vs {r['away_team']}")
        print(f"Predicted winner: {r['predicted_winner']} (confidence: {r['confidence']:.1%})")
        print(f"Probabilities: {r['probabilities']}")
        print(f"Reasoning: {r['reasoning']}")
