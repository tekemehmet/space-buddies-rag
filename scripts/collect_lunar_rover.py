from collector_common import collect_sources


SOURCES = [
    {
        "id": "lunar-rover-overview",
        "title": "The Apollo Lunar Roving Vehicle",
        "url": "https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo_lrv.html",
        "topic": "overview"
    },
    {
        "id": "lunar-rover-exploration",
        "title": "History of Lunar Exploration",
        "url": "https://science.nasa.gov/solar-system/moon/history-of-lunar-exploration/",
        "topic": "mission_history"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="lunar-rover",
        explorer_name="Lunar Roving Vehicle",
        mission_family="Apollo",
        body="Moon",
        equipment_type="rover"
    )