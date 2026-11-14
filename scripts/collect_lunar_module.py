from collector_common import collect_sources


SOURCES = [
    {
        "id": "lunar-module-history",
        "title": "Apollo's Lunar Module Bridged Technological Leap to the Moon",
        "url": "https://www.nasa.gov/history/apollos-lunar-module-bridged-technological-leap-to-the-moon/",
        "topic": "engineering"
    },
    {
        "id": "apollo-program",
        "title": "The Apollo Program",
        "url": "https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo.html",
        "topic": "mission_overview"
    },
    {
        "id": "apollo-landing-sites",
        "title": "Apollo Landing Sites",
        "url": "https://science.nasa.gov/resource/apollo-landing-sites/",
        "topic": "landing_sites"
    }
]


if __name__ == "__main__":
    collect_sources(
        SOURCES,
        explorer_id="lunar-module",
        explorer_name="Apollo Lunar Module",
        mission_family="Apollo",
        body="Moon",
        equipment_type="lunar_module"
    )