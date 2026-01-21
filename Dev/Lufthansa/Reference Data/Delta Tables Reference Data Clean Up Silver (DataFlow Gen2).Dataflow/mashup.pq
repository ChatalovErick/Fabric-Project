[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_aircrafts_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_aircrafts" = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "Bronze.lufthansadata_aircrafts", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 3", {"_ingest_ts", "_source_file"}),
  #"Removed duplicates" = Table.Distinct(#"Removed columns", {"AircraftCode"})
in
  #"Removed duplicates";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_airlines_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_airlines" = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "Bronze.lufthansadata_airlines", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 3", {"_ingest_ts", "_source_file"}),
  #"Renamed columns" = Table.RenameColumns(#"Removed columns", {{"AirlineID", "AirlineCode"}}),
  #"Added index" = Table.AddIndexColumn(#"Renamed columns", "Index", 1, 1, Int64.Type),
  #"Reordered columns" = Table.ReorderColumns(#"Added index", {"Index", "AirlineCode", "AirlineID_ICAO", "AirlineName"}),
  #"Renamed columns 1" = Table.RenameColumns(#"Reordered columns", {{"Index", "AirlineID"}}),
  #"Marked key columns" = Table.AddKey(#"Renamed columns 1", {"AirlineID"}, false)
in
  #"Marked key columns";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_airports_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_airports" = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "Bronze.lufthansadata_airports", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 3", {"_ingest_ts", "_source_file"}),
  #"Renamed columns" = Table.RenameColumns(#"Removed columns", {{"AirportCode", "AirportID"}}),
  #"Renamed columns 1" = Table.RenameColumns(#"Renamed columns", {{"AirportID", "AirportCode"}}),
  #"Added index" = Table.AddIndexColumn(#"Renamed columns 1", "Index", 1, 1, Int64.Type),
  #"Reordered columns" = Table.ReorderColumns(#"Added index", {"Index", "AirportCode", "AirportName", "CityCode", "CountryCode", "LocationType", "TimeZoneId", "UtcOffset"}),
  #"Renamed columns 2" = Table.RenameColumns(#"Reordered columns", {{"Index", "AirportId"}}),
  #"Marked key columns" = Table.AddKey(#"Renamed columns 2", {"AirportId"}, false)
in
  #"Marked key columns";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_cities_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_cities" = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "Bronze.lufthansadata_cities", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 3", {"_ingest_ts", "_source_file"}),
  #"Replaced value" = Table.ReplaceValue(#"Removed columns", "[", "", Replacer.ReplaceText, {"Airports"}),
  #"Replaced value 1" = Table.ReplaceValue(#"Replaced value", "]", "", Replacer.ReplaceText, {"Airports"}),
  #"Split column by delimiter" = Table.ExpandListColumn(Table.TransformColumns(#"Replaced value 1", {{"Airports", Splitter.SplitTextByDelimiter(","), let itemType = (type nullable text) meta [Serialized.Text = true] in type {itemType}}}), "Airports"),
  #"Added index" = Table.AddIndexColumn(#"Split column by delimiter", "Index", 1, 1, Int64.Type),
  #"Changed column type" = Table.TransformColumnTypes(#"Added index", {{"Airports", type text}}),
  #"Reordered columns" = Table.ReorderColumns(#"Changed column type", {"Index", "Airports", "CityCode", "CityName", "CountryCode", "TimeZoneId", "UtcOffset"}),
  #"Renamed columns" = Table.RenameColumns(#"Reordered columns", {{"Index", "CitiesId"}}),
  #"Marked key columns" = Table.AddKey(#"Renamed columns", {"CitiesId"}, false)
in
  #"Marked key columns";
shared #"Bronze lufthansadata_aircrafts_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_aircrafts", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared #"Bronze lufthansadata_airlines_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_airlines", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared #"Bronze lufthansadata_airports_DataDestination" = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_airports", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_countries_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_countries" = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "Bronze.lufthansadata_countries", ItemKind = "Table"]}[Data],
  #"Removed duplicates" = Table.Distinct(#"Navigation 3", {"countryCode"}),
  #"Removed columns" = Table.RemoveColumns(#"Removed duplicates", {"_ingest_ts", "_source_file"})
in
  #"Removed columns";
shared #"Bronze lufthansadata_countries_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_countries", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data]{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data];
shared #"Bronze lufthansadata_cities_DataDestination" = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_cities", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
