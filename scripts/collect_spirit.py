from collector_common import collect_sources


SOURCES = [
    {
        "id": "spirit-overview",
        "title": "Spirit - NASA Science",
        "url": "https://science.nasa.gov/mission/mer-spirit/",
        "topic": "overview"
    },
    {
        "id": "spirit-mer-overview",
        "title": "Mars Exploration Rovers: Spirit and Opportunity",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/",
        "topic": "mission_overview"
    },
    {
        "id": "spirit-science-objectives",
        "title": "Mars Exploration Rovers - Science Objectives",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/science-objectives/",
        "topic": "science_objectives"
    },
    {
        "id": "spirit-science-highlights",
        "title": "Mars Exploration Rovers - Science Highlights",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/science-highlights/",
        "topic": "science_discoveries"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="spirit",
        explorer_name="Spirit",
        mission_family="Mars Exploration Rover",
        body="Mars",
        equipment_type="rover"
    )