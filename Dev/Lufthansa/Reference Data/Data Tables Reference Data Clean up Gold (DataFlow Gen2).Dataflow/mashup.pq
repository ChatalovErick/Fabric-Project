[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = let
  Source = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  #"Navigation 1" = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data]
in
  #"Navigation 2";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Silver_lufthansadata_aircrafts_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Silver_lufthansadata_aircrafts = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver_lufthansadata_aircrafts", ItemKind = "Table"]}[Data],
  #"Renamed columns" = Table.RenameColumns(#"Navigation 2", {{"AircraftCode", "Aircraft Code"}, {"AircraftName", "Aircraft Name"}}),
  #"Removed columns" = Table.RemoveColumns(#"Renamed columns", {"AirlineEquipCode"}),
  #"Renamed columns 1" = Table.RenameColumns(#"Removed columns", {{"Aircraft Code", "AircraftCode"}, {"Aircraft Name", "AircraftName"}})
in
  #"Renamed columns 1";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Silver_lufthansadata_airlines_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Silver_lufthansadata_airlines = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver_lufthansadata_airlines", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"AirlineID_ICAO"}),
  #"Renamed columns" = Table.RenameColumns(#"Removed columns", {{"AirlineCode", "AirlineCode"}, {"AirlineName", "AirlineName"}}),
  #"Removed columns 1" = Table.RemoveColumns(#"Renamed columns", {"AirlineID"}),
  #"Removed duplicates" = Table.Distinct(#"Removed columns 1", {"AirlineCode"})
in
  #"Removed duplicates";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Silver_lufthansadata_airports_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Silver_lufthansadata_airports = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver_lufthansadata_airports", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"TimeZoneId", "UtcOffset"}),
  #"Filtered rows" = Table.SelectRows(#"Removed columns", each ([LocationType] = "Airport")),
  #"Removed columns 1" = Table.RemoveColumns(#"Filtered rows", {"LocationType", "AirportId"}),
  #"Merged queries" = Table.NestedJoin(#"Removed columns 1", {"AirportCode"}, Silver_lufthansadata_cities, {"AirportCode"}, "Silver_lufthansadata_cities", JoinKind.Inner),
  #"Expanded Silver_lufthansadata_cities" = Table.ExpandTableColumn(#"Merged queries", "Silver_lufthansadata_cities", {"CityName", "countryName"}, {"CityName", "countryName"}),
  #"Renamed columns" = Table.RenameColumns(#"Expanded Silver_lufthansadata_cities", {{"countryName", "CountryName"}}),
  #"Removed duplicates" = Table.Distinct(#"Renamed columns", {"AirportCode"})
in
  #"Removed duplicates";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Silver_lufthansadata_cities_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared Silver_lufthansadata_cities = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver_lufthansadata_cities", ItemKind = "Table"]}[Data],
  #"Merged queries" = Table.NestedJoin(#"Navigation 2", {"CountryCode"}, Silver_lufthansadata_countries, {"countryCode"}, "Silver_lufthansadata_countries", JoinKind.Inner),
  #"Expanded Silver_lufthansadata_countries" = Table.ExpandTableColumn(#"Merged queries", "Silver_lufthansadata_countries", {"countryName"}, {"countryName"}),
  #"Removed columns" = Table.RemoveColumns(#"Expanded Silver_lufthansadata_countries", {"UtcOffset"}),
  #"Renamed columns" = Table.RenameColumns(#"Removed columns", {{"Airports", "Airport Code"}, {"CityCode", "City Code"}, {"CityName", "City Name"}, {"CountryCode", "Country Code"}}),
  #"Removed columns 1" = Table.RemoveColumns(#"Renamed columns", {"CitiesId", "TimeZoneId"}),
  #"Renamed columns 1" = Table.RenameColumns(#"Removed columns 1", {{"Airport Code", "AirportCode"}, {"City Code", "CityCode"}, {"City Name", "CityName"}, {"Country Code", "CountryCode"}})
in
  #"Renamed columns 1";
[BindToDefaultDestination = true]
shared Silver_lufthansadata_countries = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver_lufthansadata_countries", ItemKind = "Table"]}[Data],
  #"Removed duplicates" = Table.Distinct(#"Navigation 2", {"countryCode"})
in
  #"Removed duplicates";
shared Silver_lufthansadata_aircrafts_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Gold_lufthansadata_aircrafts", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Silver_lufthansadata_airports_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Gold_lufthansadata_airports", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Silver_lufthansadata_cities_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Gold_lufthansadata_cities", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared Silver_lufthansadata_airlines_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Gold_lufthansadata_airlines", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
