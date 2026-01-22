# Data Engineering Project: Aviation Intelligence & Safety Analysis
### 🛠 Technology Stack
![Microsoft Fabric](https://img.shields.io/badge/Microsoft%20Fabric-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Dataflow Gen2](https://img.shields.io/badge/Dataflow%20Gen2-01B8AA?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Pipelines](https://img.shields.io/badge/Pipelines-0078D4?style=for-the-badge&logo=azure-pipelines&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C80F?style=for-the-badge&logo=power-bi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)

<p align="center">
  <img width="1505" height="528" alt="image" src="https://github.com/user-attachments/assets/469c3e77-cf03-4ab8-8989-6c25a8f71954" />
  <br>
  <i><b>Figure 1:</b> Fabric Project Task Flow</i>
</p>

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

## 5. Pipeline Orchestration & Workflow
I designed a modular orchestration strategy where each data domain is governed by its own dedicated pipeline. This ensures that failures in one domain (e.g., a scraping error in Aviation Herald) do not block the processing of other domains like Flight Status.

### 5.1. Pipeline Overview
| Data Source | Description | Update Frequency | Acquisition Method |
| :--- | :--- | :--- | :--- |
| `Flight_Status` | Real-time delays & operational hub data | High Frequency (4 hours) | Lufthansa API |
| `Schedules` | Planned flight paths and route frequencies | Daily | Lufthansa API |
| `Reference_Data` | Master lists (Airports, Airlines, Aircraft) | Monthly / On-Demand | Lufthansa API |
| `Aviation_Herald Data` | Historical safety incidents & aircraft safety | Daily | Web Scraper |

### 5.2 Multi-Pipeline Execution Logic
Each pipeline follows a standardized workflow within Fabric to maintain the Medallion integrity:

+ **Ingestion Activity:** Calls a Notebook or Script to pull raw data into Bronze.
+ **Validation Gate:** A check ensures the file was written successfully before proceeding.
+ **Silver Transformation:** A PySpark Notebook flattens the JSON and enforces schemas.
+ **Gold Upsert:** The final Notebook performs a "Merge" (Upsert) operation into the Gold Delta tables to prevent duplicate records.
+ **Semantic Link:** Once the Gold table is updated, the Power BI Direct Lake mode automatically reflects the changes without requiring a separate dataset refresh.

### 5.3 Technical Benefits of this Approach
**Parallelism:** Multiple pipelines can run simultaneously, reducing the total "Time-to-Insight."
**Error Isolation:** If the Lufthansa API is down, the Aviation Herald pipeline can still finish its run.
**Resource Efficiency:** Smaller, frequent updates for Flight Status consume fewer Fabric Capacity units than a single "monolith" pipeline.

## 6. Semantic Model

<p align="center">
  <img width="817" height="636" alt="image" src="https://github.com/user-attachments/assets/3b157fdb-40aa-488c-8c46-c848e5e82a09" />
  <br>
  <i><b>Figure 2:</b> Semantic Model</i>
</p>

### 6.1 The "Activity" Tables (The Facts)
In the corners of your model, you have your Fact Tables. These are lists of things that happened:
+ **Schedules:** What we planned to do.
+ **Flight Status:** What actually happened (the real-time reality).
+ **Aviation Herald:** Any safety incidents or "events" that occurred.

### 6.2. The "Filter" Tables (The Dimensions)
The tables in the center (Date, Airports, Airlines, Aircrafts) are your Dimensions.

## 7. Challenges & Lessons Learned
During the development of this project, several technical and architectural challenges were encountered and addressed:

### 7.1 File System Design & Data Ingestion
+ **Issue:** I spent a significant amount of time designing the initial file system structure for the Aviation Herald JSON data.
+ **Impact:** This delayed the transition to the transformation phase, as the raw folder hierarchy needed to be intuitive enough to support both historical safety data and incremental updates.
+ **Resolution:** I eventually standardized a structure that separates raw scrapes by timestamp, allowing the Bronze layer to act as a reliable "Time Travel" repository for re-processing.

### 7.2 Optimization of Compute Resources (Fabric Capacity)
+ **Issue:** The pipeline relied heavily on Apache Spark for all transformation tasks, which led to high consumption of Fabric Capacity.
+ **Impact:** Processing smaller datasets or simple transformations using Spark clusters was sometimes inefficient compared to the overhead required to spin up the nodes.
+ **Lesson Learned:** For future iterations, I would utilize the Pandas library for smaller, non-distributed data transformations. Balancing Spark for large-scale Lufthansa datasets and Pandas for localized Aviation Herald processing would result in better resource management and lower costs.

### 7.3 Dataflow Gen2 & Schema Mapping
+ **Issue:** I faced difficulties using Dataflow Gen2 to transform the Aviation Herald data into the Silver and Gold layers.
+ **Impact:** It was challenging to extract and isolate the most significant columns (like specific aircraft sub-models or standardized airline names) from the semi-structured scraped data.

