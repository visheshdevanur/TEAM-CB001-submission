import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
from app.core.config import settings
from PIL import Image
import json
import re
import time

class VLMExplanationRequest(BaseModel):
    complaint_id: int
    issue_type: str
    metrics: dict
    before_image_path: str
    after_image_path: str

class VLMExplanationResponse(BaseModel):
    explanation: str
    confidence_score: float
    visual_score: int
    key_observations: List[str]
    verdict: str
    is_real_ai: bool

class VLMReasoningAssistant:
    """
    Integrates Gemini via the google-genai SDK
    to provide real visual reasoning of civic resolution evidence.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Live image comparison is unavailable.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"Initialized {settings.GEMINI_MODEL} via google-genai SDK for live visual reasoning.")
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                self.client = None

    def generate_explanation(self, request: VLMExplanationRequest) -> VLMExplanationResponse:
        if not self.client:
            return self._unavailable_response(
                "Live AI review is unavailable because GEMINI_API_KEY is not configured on the backend."
            )

        try:
            print(f"VLM: Processing complaint {request.complaint_id}...")
            img_before = Image.open(request.before_image_path)
            img_after = Image.open(request.after_image_path)

            prompt = f"""
You are reviewing a municipal before/after evidence pair for: {request.issue_type}.

The selected complaint category is mandatory. First inspect BOTH photos and decide whether
they actually show this category. If either photo primarily shows a different type of civic
issue (for example, a pothole submitted as garbage_accumulation), return CATEGORY_MISMATCH.
Do not score resolution for a category mismatch.

First decide whether these photos show the SAME physical location and the SAME reported issue.
If they are different scenes, unrelated subjects, or there are not enough matching landmarks,
you MUST return DIFFERENT_SCENE or INCONCLUSIVE. Do not infer that a problem was fixed from
different pictures.

Only if the location and issue are comparable, decide whether the issue is RESOLVED,
PARTIALLY_RESOLVED, or NOT_RESOLVED. Use only what is visually visible. The deterministic
pipeline metrics below are secondary evidence and may be wrong; the images take priority:
{request.metrics}

Give a visual evidence score from 0 to 100 based ONLY on the two images:
- 90-100: same scene clearly confirmed and the issue is visibly resolved.
- 60-89: same scene confirmed but resolution is partial or uncertain.
- 0-59: issue persists, scenes differ, or evidence is inadequate.
- 0: the selected complaint category does not match the visual evidence.
The score is not a claim of certainty; reflect ambiguity with a lower score.

Return exactly one JSON object with this shape and no markdown:
{{"verdict":"RESOLVED|PARTIALLY_RESOLVED|NOT_RESOLVED|CATEGORY_MISMATCH|DIFFERENT_SCENE|INCONCLUSIVE",
  "explanation":"plain-language evidence statement", "observations":["observation"],
  "confidence":0.0, "visual_score":0}}
            """

            print("VLM: Calling Gemini API...")
            response = None
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[prompt, img_before.convert("RGB"), img_after.convert("RGB")],
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    break
                except Exception as error:
                    if attempt == 2:
                        raise
                    print(f"VLM: temporary API failure ({error}); retrying...")
                    time.sleep(2 ** attempt)

            if not response or not response.text:
                print("VLM: Gemini returned an empty response.")
                return self._unavailable_response()

            full_text = response.text.strip()
            print(f"VLM: Success! Received: {full_text[:100]}...")

            data = self._parse_response(full_text)
            return VLMExplanationResponse(
                explanation=data["explanation"],
                confidence_score=data["confidence"],
                visual_score=data["visual_score"],
                key_observations=data["observations"],
                verdict=data["verdict"],
                is_real_ai=True
            )

        except Exception as e:
            print(f"VLM CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                return self._unavailable_response(
                    "Gemini’s current image-analysis quota has been reached. This complaint is queued for AI review when the quota is available again."
                )
            return self._unavailable_response(
                "Gemini image analysis did not complete. Check the backend GEMINI_API_KEY, Gemini model, and quota configuration."
            )

    def _parse_response(self, text: str) -> dict:
        clean_text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        data = json.loads(clean_text)
        allowed = {"RESOLVED", "PARTIALLY_RESOLVED", "NOT_RESOLVED", "CATEGORY_MISMATCH", "DIFFERENT_SCENE", "INCONCLUSIVE"}
        verdict = str(data.get("verdict", "INCONCLUSIVE")).upper()
        if verdict not in allowed:
            verdict = "INCONCLUSIVE"
        visual_score = max(0, min(100, int(float(data.get("visual_score", 0)))))
        if verdict == "CATEGORY_MISMATCH":
            visual_score = 0
        return {
            "verdict": verdict,
            "explanation": str(data.get("explanation") or "The AI could not reach a reliable conclusion."),
            "observations": [str(item) for item in data.get("observations", [])][:5],
            "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            "visual_score": visual_score
        }

    def _unavailable_response(self, explanation: str = "A live image-model assessment was unavailable, so no resolution conclusion was made.") -> VLMExplanationResponse:
        return VLMExplanationResponse(
            explanation=explanation,
            confidence_score=0.0,
            visual_score=0,
            key_observations=[],
            verdict="INCONCLUSIVE",
            is_real_ai=False
        )

vlm_assistant = VLMReasoningAssistant()
