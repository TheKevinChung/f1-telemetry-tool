# Formula 1 Speed, Tire Degradation, and Braking Analysis Tool

**Live app:** https://f1-telemetry-tool.streamlit.app/

A web tool for comparing two drivers within a single Formula 1 race across four dimensions: fastest-lap speed traces, the time gap between them around the lap, and how quickly their tires degrade by compound. Built with Python, FastF1, Plotly, and Streamlit.

## How to Use

Pick a season (2018 onward), then a race from that season's calendar, then any two drivers who competed in it. The tool generates a speed overlay, a time-gap chart, and a tire-degradation comparison for the two drivers.

## Speed and Time-Gap Analysis

The speed and time-gap analysis in the Formula 1 telemetry tool takes in the fastest lap of two drivers and compares them across the lap. The tool pulls each driver's speed throughout the lap and calculates the time gap between them through subtraction, then plots the difference in time over the course of the lap. Since the two drivers can be at different points on the track and the sensors in their cars record data at different intervals, the tool builds a shared grid of 1000 evenly spaced distance points and interpolates each driver's speed onto it to keep the data standardized. This way, at any given point — 500 meters into the lap, for instance — both drivers are measured at the same physical spot. The delta (the change in time) is then calculated by finding the per-segment time (distance / speed), subtracting one driver from the other, and taking a cumulative sum across the lap.

This analysis carries some confounding variables. For example, Formula 1 cars differ in performance because they are designed differently, which creates speed differences the driver cannot control. In other words, if two different teams ran the same driver, their times would still vary, since the car itself affects the pace. Additionally, the FastF1 API only provides data from the 2018 season onward, so any race before 2018 is not included in the tool.

## Tire Degradation Analysis

This tool pulls lap-level race data from the FastF1 API — lap times, lap number, tire compound, and stint — for any two drivers in a given race from recent sessions. Using the data, the tool measures how each driver's pace evolved during their stint on a given tire compound. For each compound, it fits a linear regression line to lap times across the stint. The slope of that line is calculated by comparing the change of pace over the stint. A driver may lose or gain time each lap, which shows who held their pace more efficiently.

There are some confounding variables, specifically a lack of data in the API, that limit the tool to providing data on net pace evolution rather than pure tire degradation as intended. For instance, as fuel burns throughout a race, the car lightens, making it faster. Additionally, track evolution (rubber laid down on the track that provides more grip) and deliberate pace management by the driver are not accounted for in this tool.

**How the functions work:** There are four main functions that return the calculated data. The first, `get_driver_laps`, takes in the two abbreviated driver names input by the user and pulls the data from the API. Then `clean_data` filters for the data that is wanted and removes outlier laps such as starts, pit stops, and exits, keeping only green-flagged or yellow-flagged laps. The tool purposefully voids red flags, virtual safety cars, safety cars, and full course yellows, as they often hinder lap times significantly. The lap time is then transformed into a seconds format for easier use. The filtered data goes to the `fit` function, which separates the valid rows by tire compound, since each tire set has a different degradation rate. Lastly, the data is sent to the `compare` function to compare the two drivers and conclude which driver loses more time over a stint.

**Design choices:** The tool purposefully splits the data by tire compound, as each compound degrades at a different rate. For instance, the fastest tire (SOFT) has immense speed but a short lifespan, while the HARD tire has slightly slower overall pace but a much longer lifespan. The tool also requires a minimum stint length (3 laps) to be considered, since a slope drawn from only three points is inaccurate.

## Braking Zone Analysis
This part of the tool breaks the lap down corner by corner to show where one driver gains or loses time on the other. It detects braking zones from one reference driver's fastest lap, using the car's brake telemetry (an on/off signal) to find continuous stretches where the driver is braking — each zone roughly corresponds to a corner, since drivers brake on corner entry. It then measures how much the time gap (delta) from the speed analysis changed across each zone. Because the delta is cumulative, that change shows how much time a driver gained or lost through that specific corner.
This approach has limits. The zones come from one reference driver, but two drivers don't brake at exactly the same points, so the boundaries are an approximation (though measuring across a window, rather than a single point, smooths out most of that difference). And because the delta is cumulative, a driver who is simply faster overall may show gains across most zones, reflecting net pace rather than purely corner-specific performance.
How the functions work: brake_detect pulls the reference driver's brake telemetry and walks through it tracking transitions — recording a zone's start when braking begins and closing it as a (start, end) pair when braking ends. brake_delta then finds the closest points on the shared distance grid to each zone's start and end, and subtracts the delta at those two points to get the time gained or lost through that zone.




