
# Shared PIP voice for all explorer chatbot responses
PIP_VOICE = "en-US-GuyNeural"


EXPLORERS = {
    "opportunity": {
        "name": "Opportunity",
        "description": "NASA's Mars exploration rover",
        "voice": PIP_VOICE,
    },
    "spirit": {
        "name": "Spirit",
        "description": "NASA's Mars exploration rover",
        "voice": PIP_VOICE,
    },
    "insight": {
        "name": "InSight",
        "description": "NASA's Mars lander that studied the interior of Mars",
        "voice": PIP_VOICE,
    },
    "ingenuity": {
        "name": "Ingenuity",
        "description": "NASA's Mars helicopter",
        "voice": PIP_VOICE,
    },
    "lunar-module": {
        "name": "Apollo Lunar Module",
        "description": "The spacecraft that landed astronauts on the Moon",
        "voice": PIP_VOICE,
    },
    "lunar-rover": {
        "name": "Lunar Roving Vehicle",
        "description": "The electric vehicle astronauts drove on the Moon",
        "voice": PIP_VOICE,
    },
}


def get_explorer(explorer_id: str) -> dict:
    if explorer_id not in EXPLORERS:
        raise ValueError(
            f"Unknown explorer: {explorer_id}. "
            f"Valid explorers: {', '.join(EXPLORERS)}"
        )

    return EXPLORERS[explorer_id]
