from collector_common import collect_sources


SOURCES = [
    {
        "id": "ingenuity-overview",
        "title": "Ingenuity Mars Helicopter - NASA Science",
        "url": "https://science.nasa.gov/mission/mars-2020-perseverance/ingenuity-mars-helicopter/",
        "topic": "overview"
    },
    {
        "id": "ingenuity-by-numbers",
        "title": "Ingenuity Mars Helicopter By the Numbers",
        "url": "https://science.nasa.gov/resource/ingenuity-mars-helicopter-by-the-numbers/",
        "topic": "mission_highlights"
    },
    {
        "id": "ingenuity-extreme-flights",
        "title": "The Most Extreme Flights of Ingenuity",
        "url": "https://science.nasa.gov/resource/mars-report-the-most-extreme-flights-of-nasas-ingenuity-mars-helicopter/",
        "topic": "flight_history"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="ingenuity",
        explorer_name="Ingenuity",
        mission_family="Mars 2020",
        body="Mars",
        equipment_type="helicopter"
    )