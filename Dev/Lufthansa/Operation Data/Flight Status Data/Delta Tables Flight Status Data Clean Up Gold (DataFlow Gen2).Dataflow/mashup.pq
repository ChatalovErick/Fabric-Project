[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data]{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data];
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Silver lufthansadata_germany_flight_status_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Silver lufthansadata_germany_flight_status" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Silver.lufthansadata_germany_flight_status", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"ServiceType", "AircraftReg"}),
  #"Removed duplicates" = Table.Distinct(#"Removed columns", {"FlightNumber","ScheduledDepartureTime","ScheduledArrivalTime"}),
  #"Removed columns 1" = Table.RemoveColumns(#"Removed duplicates", {"FlightStatusId"}),
  #"Inserted Date" = Table.AddColumn(#"Removed columns 1", "ScheduledArrivalDate", each Date.From([ScheduledArrivalTime]), type date),
  #"Inserted Date 1" = Table.AddColumn(#"Inserted Date", "ScheduledDepartureDate", each Date.From([ActualArrivalTime]), type date),
  #"Reordered columns" = Table.ReorderColumns(#"Inserted Date 1", {"AircraftCode", "ActualArrivalTime", "ScheduledArrivalTime", "ScheduledArrivalDate", "ArrivalStatus", "Carrier", "ActualDepartureTime", "ScheduledDepartureTime", "ScheduledDepartureDate", "DepartureStatus", "Destination", "FlightNumber", "FlightStatus", "Origin", "MovementType", "_ingest_ts"})
in
  #"Reordered columns";
shared #"Silver lufthansadata_germany_flight_status_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Gold_lufthansadata_germany_flight_status", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
