from cities import cities


def main():
    with open("README.md", "r") as f:
        readme_contents = f.readlines()

    # Find the start and end indices of the table you want to replace
    table_start = None
    table_end = None
    for i, line in enumerate(readme_contents):
        if line.startswith("| Country"):
            table_start = i
        elif ".geojson" in line and table_start is not None:
            table_end = max(i, table_end or 0)

    # Make sure the table was found
    if table_start is None or table_end is None:
        raise RuntimeError("Table not found in README.md")

    # Generate the new table content
    new_table = []
    new_table.append("| Country | Name | Stations (live) | Weather (live) |\n")
    new_table.append("|---------|------|-----------------|----------------|\n")
    for city in sorted(cities, key=lambda c: c.country + c.name):
        new_table.append(
            f"| {city.country} | {city.name} | [`{city.name}.geojson`](data/stations/{city.name}.geojson) | [`{city.name}.json`](data/weather/{city.name}.json) |\n"
        )

    # Replace the existing table with the new table
    readme_contents[table_start : table_end + 1] = new_table

    # Write the modified contents back to the README.md file
    with open("README.md", "w") as f:
        f.writelines(readme_contents)


if __name__ == "__main__":
    main()
