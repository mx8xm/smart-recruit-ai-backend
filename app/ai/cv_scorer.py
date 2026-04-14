from sentence_transformers import util
from app.ai.model_loader import get_scoring_model
import logging

logger = logging.getLogger(__name__)

def calculate_match_score(job_description: str, cv_text: str) -> float:
    """
    Calculate semantic similarity between job description and CV
    
    Args:
        job_description: The job description text
        cv_text: The candidate's CV text
        
    Returns:
        Match score between 0.0 and 1.0
    """
    if not job_description or not cv_text:
        logger.warning("Empty job description or CV text")
        return 0.0
    
    logger.info("🎯 Calculating match score...")
    
    try:
        model = get_scoring_model()
        
        # Encode both texts
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        cv_embedding = model.encode(cv_text, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cosine_score = util.pytorch_cos_sim(job_embedding, cv_embedding)
        score = round(cosine_score.item(), 3)
        
        logger.info(f"✅ Match score calculated: {score * 100:.2f}%")
        
        return score
        
    except Exception as e:
        logger.error(f"❌ Score calculation failed: {e}")
        return 0.0
