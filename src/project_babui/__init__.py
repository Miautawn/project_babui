from pathlib import Path

from dotenv import load_dotenv
from humanization import HumanizationConfig

load_dotenv()

state_file = Path(__file__).parent.parent.parent / "state.json"
chromium_url = "http://localhost:9222"
humanization_config = HumanizationConfig(
    fast=True,
    humanize=True,
    characters_per_minute=400,
    backspace_cpm=800,
    timeout=2000,
    stealth_mode=True,
)
candidate_threshold = 4
