
EXPLORERS = {
    "opportunity": {
        "name": "Opportunity",
        "description": "NASA's Mars exploration rover",
        "voice": "en-US-JennyNeural",
    },
    "spirit": {
        "name": "Spirit",
        "description": "NASA's Mars exploration rover",
        "voice": "en-US-AriaNeural",
    },
    "insight": {
        "name": "InSight",
        "description": "NASA's Mars lander that studied the interior of Mars",
        "voice": "en-US-GuyNeural",
    },
    "ingenuity": {
        "name": "Ingenuity",
        "description": "NASA's Mars helicopter",
        "voice": "en-US-AnaNeural",
    },
    "lunar-module": {
        "name": "Apollo Lunar Module",
        "description": "The spacecraft that landed astronauts on the Moon",
        "voice": "en-US-DavisNeural",
    },
    "lunar-rover": {
        "name": "Lunar Roving Vehicle",
        "description": "The electric vehicle astronauts drove on the Moon",
        "voice": "en-US-AndrewNeural",
    },
}


def get_explorer(explorer_id: str) -> dict:
    if explorer_id not in EXPLORERS:
        raise ValueError(
            f"Unknown explorer: {explorer_id}. "
            f"Valid explorers: {', '.join(EXPLORERS)}"
        )

    return EXPLORERS[explorer_id]
