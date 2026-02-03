import os

# GLM 4.7 Configuration
GLM_API_KEY = os.environ.get("GLM_API_KEY")
GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
GLM_MODEL = "glm-4-plus"  # or "glm-4" — adjust to your access tier

# Token budgets per layer
TOKEN_BUDGETS = {
    "business": 2000,
    "product": 3000,
    "technical": 3000,
    "implementation": 2000
}

# Confidence thresholds
MIN_CONFIDENCE_TO_PROCEED = 0.7
PROBE_PASS_BOOST = 0.1
PROBE_FAIL_PENALTY = 0.2
