# Data Engineering Project: Aviation Intelligence & Safety Analysis

## 1. Project Objectives
The goal of this project is to build an end-to-end data pipeline that correlates real-time flight operations with historical safety records to provide a holistic view of airline performance. This project analyzes the aviation landscape within Germany, specifically focusing on major hubs (Frankfurt, Munich, Berlin, etc.). By correlating real-time flight status from Lufthansa with historical safety events from the Aviation Herald

### 1.1 Key Questions to Answer:

+ **Operational Efficiency:**: What is the average arrival and departure delay for major hubs like Frankfurt (FRA)?
+ **Route Popularity:**: Which destinations have the highest frequency of scheduled flights from specific origins (e.g., Berlin)?
+ **Safety Correlation:**: Is there a relationship between specific aircraft models (e.g., B738 or A321) and the frequency of reported incidents in the Aviation Herald?
+ **Airline Comparison:** How does Lufthansa's flight volume compare to its competitors (Eurowings, Austrian, etc.) relative to their historical accident counts?

## 2. Data Sources
+ **Lufthansa Developer Center:** Used for real-time Flight Status (delays, arrival/departure times) and Schedule Data (planned routes and durations):
  + https://developer.lufthansa.com/
+ **The Aviation Herald:** Scraped or ingested historical data regarding flight accidents, crashes, and incidents categorized by aircraft type and airline:
  + https://avherald.com/
 

## 3. The Medallion Architecture in Microsoft Fabric
To manage the data lifecycle, I implemented a Medallion Architecture within a single Fabric Lakehouse. This approach ensures that data is incrementally refined, providing a clear audit trail from raw API responses to the final dashboard. While Dataflow Gen2 was used for the logic of cleaning and transforming, PySpark Notebooks served as the orchestration engine to move and save data between the different layers.

### 3.1 Layer 1: Bronze (The Raw Zone)
This layer acts as the landing zone for all ingested data in its original format to ensure no information is lost.

+ **Aviation Herald Data:** Stored as raw JSON files following the web scraping process.
+ **Lufthansa Developer Center:** Ingested in both JSON and Delta Parquet formats.
+ **Role:** Provides a "Source of Truth" that allows for data reprocessing without re-querying external APIs or re-scraping websites.

### 3.2 Layer 2: Silver (The Validated Zone)
In this layer, the data is cleaned and structured into a queryable format.

+ **Parsing & Flattening:** JSON structures are flattened into tabular formats using PySpark notebooks.
+ **Data Consistency:** Aligning and standardizing key identifiers and entity names across both the Lufthansa and Aviation Herald datasets.
+ **Schema Enforcement:** Converting string-based timestamps into proper datetime objects.

### 3.3 Layer 3: Gold (The Business Zone)
The Gold layer contains the final, high-performance tables optimized for analytics.

+ **Star Schema Design:** Data is organized into "fact tables" and "Dimension tables".
+ **Semantic Model Integration:** These tables are used to build the Power BI Semantic Model, enabling the high-speed filtering and gauge visualizations seen in the report.

## 4. Data Transformation Logic

### 4.1. Aviation Herald (Safety Data)
- **Bronze:** Raw scraped JSON files containing incident logs.

- **Silver:** Parsing: Split the unstructured "Events" text into dedicated columns: Date, Airline Name, Aircraft Code, and Event Description.

- **Integrity:** Added a surrogate primary key called EventId.

- **Quality:** Performed a global deduplication check.

- **Gold:** Refinement: Removed the EventId (as it's no longer needed for the reporting layer) and performed a final deduplication to ensure safety metrics are unique.

### 4.2. Flight Status Data
- **Bronze:** JSON and Delta Parquet files from the Lufthansa API.

- **Silver:** Split into two distinct tables:
   + **Flight_Status:** Contains operational data (delays, timing).
   + **Airport_Connections:** Captures existing flight paths from German hubs to be used for future schedule lookups.

- **Cleaning:** Added index columns, removed irrelevant metadata columns, and standardized all date/time fields.

- **Gold:** Optimization: Removed indices and high-cardinality "unimportant" columns.

- **Semantic Readiness:** Created separate Date columns from DateTime fields to support Power BI date slicers and time-intelligence calculations.

### 4.3. Flight Schedules
- **Bronze:** Daily schedules gathered based on the routes identified in Airport_Connections.

- **Silver:** Renamed columns for readability, standardized data types, and added an index for primary key tracking.

- **Gold:** Filtered for unique records and generated specific Arrival Date and Departure Date columns for the semantic model.

### 4.4. Reference Tables (Master Data)
I extracted master data for Airports, Airlines, Cities, Countries, and Aircraft types from the Lufthansa Developer Center.

- **Silver:** Standardized naming conventions, removed duplicates, and added index columns for all tables except Countries.

- **Gold (The Master Merge):**  The "Airports" Master Table: Merged Countries, Cities, and Airports into a single, comprehensive dimension table.

- **Clean Room:** Removed all temporary indices and unnecessary columns, leaving a lean, deduplicated master list for the Power BI model.

### 4.5 Technical Choice (Notebooks for Layer Transfers)
I chose to use Notebooks to move data between layers because they provide better control over Delta Lake features. Using Spark commands ensures that the Gold layer tables are always optimized and ready for the
Power BI Direct Lake connection, which is faster than traditional Import methods.

## 5. Challenges & Lessons Learned
During the development of this project, several technical and architectural challenges were encountered and addressed:

### 5.1 File System Design & Data Ingestion
+ **Issue:** I spent a significant amount of time designing the initial file system structure for the Aviation Herald JSON data.
+ **Impact:** This delayed the transition to the transformation phase, as the raw folder hierarchy needed to be intuitive enough to support both historical safety data and incremental updates.
+ **Resolution:** I eventually standardized a structure that separates raw scrapes by timestamp, allowing the Bronze layer to act as a reliable "Time Travel" repository for re-processing.

### 5.2 Optimization of Compute Resources (Fabric Capacity)
+ **Issue:** The pipeline relied heavily on Apache Spark for all transformation tasks, which led to high consumption of Fabric Capacity.
+ **Impact:** Processing smaller datasets or simple transformations using Spark clusters was sometimes inefficient compared to the overhead required to spin up the nodes.
+ **Lesson Learned:** For future iterations, I would utilize the Pandas library for smaller, non-distributed data transformations. Balancing Spark for large-scale Lufthansa datasets and Pandas for localized Aviation Herald processing would result in better resource management and lower costs.

### 5.3 Dataflow Gen2 & Schema Mapping
+ **Issue:** I faced difficulties using Dataflow Gen2 to transform the Aviation Herald data into the Silver and Gold layers.
+ **Impact:** It was challenging to extract and isolate the most significant columns (like specific aircraft sub-models or standardized airline names) from the semi-structured scraped data.

# 6. Final Insights (From Dashboard)
+ **Reliability:** Frankfurt (FRA) currently maintains an average arrival delay of 3.87, with the majority of flights being Early (30 flights) or On Time (16 flights).
+ **Schedule Volume:** Munich (MUC) is the top destination with 57 scheduled flights, followed by Frankfurt (FRA) with 52.
+ **Safety Trends:** The B738 and A21N aircraft types show the highest historical accident counts in the Aviation Herald dataset, providing a critical safety lens for operational data.
