[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data]{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data];
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze lufthansadata_germany_schedule_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze lufthansadata_germany_schedule" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Bronze.lufthansadata_germany_schedule", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"_source_file", "_ingest_ts", "timestamp"}),
  #"Added index" = Table.AddIndexColumn(#"Removed columns", "Index", 1, 1, Int64.Type),
  #"Reordered columns" = Table.ReorderColumns(#"Added index", {"Index", "Flight_Number", "Aircraft", "Origin", "Destination", "Departure_Time", "Arrival_Time", "Duration", "Has_Wifi"}),
  #"Renamed columns" = Table.RenameColumns(#"Reordered columns", {{"Index", "ScheduleId"}, {"Flight_Number", "FlightNumber"}, {"Departure_Time", "DepartureTime"}, {"Arrival_Time", "ArrivalTime"}}),
  #"Marked key columns" = Table.AddKey(#"Renamed columns", {"ScheduleId"}, false),
  #"Changed column type" = Table.TransformColumnTypes(#"Marked key columns", {{"DepartureTime", type datetime}, {"ArrivalTime", type datetime}, {"Duration", type text}}),

  // --- NEW STEPS START HERE ---

  // 1. Filter out the Lufthansa Express Rail (Trains)
  #"Filtered Trains" = Table.SelectRows(#"Changed column type", each ([Aircraft] <> "TRS")),

  // 2. Add the Duration Calculation Logic
  #"Added DurationMinutes" = Table.AddColumn(#"Filtered Trains", "DurationMinutes", each 
    let
        // Remove P and T prefixes (e.g., PT1H5M -> 1H5M)
        Clean = Text.Remove([Duration], {"P", "T"}),
        
        // Extract Hours
        Hours = if Text.Contains(Clean, "H") 
                then Number.From(Text.BeforeDelimiter(Clean, "H")) 
                else 0,
        
        // Extract Minutes (handle cases with and without Hours)
        Remaining = if Text.Contains(Clean, "H") 
                    then Text.AfterDelimiter(Clean, "H") 
                    else Clean,
        Minutes = if Text.Contains(Remaining, "M") 
                  then Number.From(Text.BeforeDelimiter(Remaining, "M")) 
                  else 0
    in
        (Hours * 60) + Minutes, Int64.Type),
  #"Removed columns 1" = Table.RemoveColumns(#"Added DurationMinutes", {"Duration"})

in
  #"Removed columns 1";
shared #"Bronze lufthansadata_germany_schedule_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_lufthansadata_germany_schedule", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
