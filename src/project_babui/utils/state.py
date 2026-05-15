import json
import os


class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self._state = self.load_state()

    @property
    def blacklist(self) -> list:
        return self._state.get("blacklist", [])

    @property
    def candidates(self) -> list:
        return self._state.get("candidates", [])

    def load_state(self) -> dict:
        if not os.path.exists(self.state_file):
            return {"blacklist": [], "candidates": []}
        else:
            with open(self.state_file, "r") as f:
                return json.load(f)

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self._state, f)

    def add_to_candidates(self, listing_id: str):
        if listing_id not in self.candidates:
            self._state["candidates"].append(listing_id)

        if listing_id not in self.blacklist:
            self._state["blacklist"].append(listing_id)

        self.save_state()
