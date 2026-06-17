FastF1 Tire Degredation Analysis Tool
Video Demo - https://youtu.be/2Rz8va_j80k
Description:

This tool pulls lap-level race data from the FastF1 API - lap times, lap number, tire compound, and stint - for any two drivers in 
a given race from recent sessions. Using the data, the tool measures how each driver's pace evolved during their stint on a given
tire compound. 

For each compound, it fits a linear regression line to lap times across the stint. The slope of that line is calculated through comparing
the change of pace over the stint. A driver may lose or gain time each lap which shows who held their pace more efficiently. 

Unfortunately, there are some confounding variables, specifically a lack of data in the API, that limits the tool to only provide data 
on the net pace evolution and not pure tire degradation as intended. For instance, as fuel burns throughout a race, the car lightens,
making it faster. Additionally, track evolution (rubber parts laid on the track to provide more grip) and deliberate pace management 
by the driver and not considered for in this tool. 

How the Function Works: There are four main functions that return the calculated data to the main function. The first being "get_driver_laps"
which takes in the two abbreviated driver names inputted by the user and pulls the data from the API. Then "clean_data" filters what
data is wanted and removes outlier laps such as starts, pit stops and exits, and only laps that are green flagged or yellow flagged. The tool
purposefully voids red flags, virtual safety cars, safety cars, and full course yellows as they often hinder lap times significantly. Additionally,
the lap time is then transformed into a seconds format for easier use. The filtered data then goes to the "fit" function in order to
separate the valid rows with tire compounds each each tire set has different degradation rates. Lastly, all this data gets sent to the
"compare" function to compare the two drivers and make a conclusion on which driver loses more time over a stint. 

Design Choices: The tool purposefully splits the data through different tire compounds as each compound of tire degrades at different
speeds. For instance, the fastest tire (SOFT) has immense speed but a short lifespan. On the contrary, the (HARD) tire has slightly slower
overall speed but a much longer lifespan. The tool also has minimum laps of a stint (3), in order to be considered data as a slope of
three points is inaccurate. 





