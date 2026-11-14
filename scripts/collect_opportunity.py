from collector_common import collect_sources


SOURCES = [
    {
        "id": "opportunity-overview",
        "title": "Opportunity - NASA Science",
        "url": "https://science.nasa.gov/mission/mer-opportunity/",
        "topic": "overview"
    },
    {
        "id": "opportunity-mer-overview",
        "title": "Mars Exploration Rovers: Spirit and Opportunity",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/",
        "topic": "mission_overview"
    },
    {
        "id": "opportunity-science-objectives",
        "title": "Mars Exploration Rovers - Science Objectives",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/science-objectives/",
        "topic": "science_objectives"
    },
    {
        "id": "opportunity-science-highlights",
        "title": "Mars Exploration Rovers - Science Highlights",
        "url": "https://science.nasa.gov/mission/mars-exploration-rovers-spirit-and-opportunity/science-highlights/",
        "topic": "science_discoveries"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="opportunity",
        explorer_name="Opportunity",
        mission_family="Mars Exploration Rover",
        body="Mars",
        equipment_type="rover"
    )