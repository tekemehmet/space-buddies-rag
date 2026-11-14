from collector_common import collect_sources


SOURCES = [
    {
        "id": "insight-overview",
        "title": "InSight Lander - NASA Science",
        "url": "https://science.nasa.gov/mission/insight/",
        "topic": "overview"
    },
    {
        "id": "insight-science",
        "title": "InSight Science",
        "url": "https://science.nasa.gov/mission/insight/science/",
        "topic": "science_objectives"
    },
    {
        "id": "insight-science-highlights",
        "title": "InSight Science Highlights",
        "url": "https://science.nasa.gov/mission/insight/science-highlights/",
        "topic": "science_discoveries"
    },
    {
        "id": "insight-instruments",
        "title": "InSight Science Instruments",
        "url": "https://science.nasa.gov/mission/insight/science-instruments/",
        "topic": "instruments"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="insight",
        explorer_name="InSight",
        mission_family="InSight",
        body="Mars",
        equipment_type="lander"
    )