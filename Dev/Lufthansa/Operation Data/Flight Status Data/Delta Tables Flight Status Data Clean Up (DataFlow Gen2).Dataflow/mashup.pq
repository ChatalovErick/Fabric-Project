[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data]{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data];
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_germany_airport_connections_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_germany_airport_connections" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Bronze.lufthansadata_germany_airport_connections", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"_ingest_ts", "_source_file"}),
  #"Added index" = Table.AddIndexColumn(#"Removed columns", "Index", 1, 1, Int64.Type),
  #"Renamed columns" = Table.RenameColumns(#"Added index", {{"Index", "Connection_Id"}})
in
  #"Renamed columns";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_germany_flight_status_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_germany_flight_status" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Bronze.lufthansadata_germany_flight_status", ItemKind = "Table"]}[Data],
  #"Added index" = Table.AddIndexColumn(#"Navigation 2", "Index", 0, 1, Int64.Type),
  #"Removed columns" = Table.RemoveColumns(#"Added index", {"Arr_Terminal", "Dep_Gate", "Dep_Terminal", "_source_file"}),
  #"Renamed columns" = Table.RenameColumns(#"Removed columns", {{"Arr_Actual", "ActualArrivalTime"}, {"Arr_Estimated", "EstimatedArrivalTime"}, {"Arr_Scheduled", "ScheduledArrivalTime"}, {"Arr_Status", "ArrivalStatus"}, {"Dep_Actual", "ActualDepartureTime"}, {"Dep_Scheduled", "ScheduledDepartureTime"}, {"Dep_Status", "DepartureStatus"}, {"type", "MovementType"}, {"Aircraft_Reg", "AircraftReg"}, {"Aircraft_Code", "AircraftCode"}, {"Flight_Number", "FlightNumber"}, {"Flight_Status", "FlightStatus"}, {"Service_Type", "ServiceType"}}),
  #"Reordered columns" = Table.ReorderColumns(#"Renamed columns", {"Index", "AircraftCode", "AircraftReg", "ActualArrivalTime", "EstimatedArrivalTime", "ScheduledArrivalTime", "ArrivalStatus", "Carrier", "ActualDepartureTime", "ScheduledDepartureTime", "DepartureStatus", "Destination", "FlightNumber", "FlightStatus", "Origin", "ServiceType", "MovementType"}),
  #"Removed columns 1" = Table.RemoveColumns(#"Reordered columns", {"EstimatedArrivalTime"}),
  #"Renamed columns 1" = Table.RenameColumns(#"Removed columns 1", {{"Index", "FlightStatusId"}}),
  #"Marked key columns" = Table.AddKey(#"Renamed columns 1", {"FlightStatusId"}, false),
  #"Reordered columns 1" = Table.ReorderColumns(#"Marked key columns", {"FlightStatusId", "AircraftCode", "AircraftReg", "ActualArrivalTime", "ScheduledArrivalTime", "ArrivalStatus", "Carrier", "ActualDepartureTime", "ScheduledDepartureTime", "DepartureStatus", "Destination", "FlightNumber", "FlightStatus", "Origin", "ServiceType", "MovementType", "_ingest_ts"}),
  #"Sorted rows" = Table.Sort(#"Reordered columns 1", {{"_ingest_ts", Order.Descending}}),
  #"Changed column type" = Table.TransformColumnTypes(#"Sorted rows", {{"ActualArrivalTime", type datetime}, {"ScheduledArrivalTime", type datetime}, {"ActualDepartureTime", type datetime}, {"ScheduledDepartureTime", type datetime}}),
  #"Removed duplicates" = Table.Distinct(#"Changed column type", {"FlightNumber","ScheduledArrivalTime","ScheduledDepartureTime"})
in
  #"Removed duplicates";
shared #"Bronze lufthansadata_germany_airport_connections_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_germany_airport_connections", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
shared #"Bronze lufthansadata_germany_flight_status_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_germany_flight_status", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
