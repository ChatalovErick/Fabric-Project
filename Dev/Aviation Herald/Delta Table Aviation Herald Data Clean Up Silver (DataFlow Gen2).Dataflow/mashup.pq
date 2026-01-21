[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data]{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data];
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Bronze aviationheralddata_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Bronze aviationheralddata" = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "Bronze.aviationheralddata", ItemKind = "Table"]}[Data],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 2", {"Year", "Month"}),
  #"Sorted rows" = Table.Sort(#"Removed columns", {{"timestamp", Order.Descending}}),
  #"Inserted Text Between Delimiters" = Table.AddColumn(#"Sorted rows", "Text Between Delimiters", each Text.BetweenDelimiters([headline], " on ", ","), type text),
  #"Inserted Text Before Delimiter" = Table.AddColumn(#"Inserted Text Between Delimiters", "Group", each Text.BeforeDelimiter([headline], " "), type text),
  #"Renamed columns" = Table.RenameColumns(#"Inserted Text Before Delimiter", {{"Text Between Delimiters", "date"}}),
  #"Added custom" = Table.AddColumn(#"Renamed columns", "Custom", each let
    Source = [headline],
    // 1. Split into words
    Words = Text.Split(Source, " "),

    // 2. Find the FIRST word that is exactly 4 characters long 
    // AND has at least one number in it.
    TargetWord = List.First(List.Select(Words, each 
        Text.Length(_) = 4 and 
        Text.Select(_, {"0".."9"}) <> ""
    )),

    // 3. Find the position, but use a default of 0 to prevent -1 errors
    Pos = List.PositionOf(Words, TargetWord),

    // 4. Combine words before that position. 
    // If no 4-char code is found, it returns the first word as a safety fallback.
    Result = if Pos > 0 then 
                Text.Combine(List.FirstN(Words, Pos), " ") 
             else 
                Words{0} 
in
    Result),
  #"Removed columns 1" = Table.RemoveColumns(#"Added custom", {"Group"}),
  #"Renamed columns 1" = Table.RenameColumns(#"Removed columns 1", {{"Custom", "Location"}}),
  #"Inserted Text Between Delimiters 1" = Table.AddColumn(#"Renamed columns 1", "Aircraft Code", each let
    // 1. Clean the input: Remove punctuation and split into words
    Source = [headline],
    CleanText = Text.Remove(Text.From(Source ?? ""), {",", ".", "!", ";", "(", ")"}),
    Words = Text.Split(CleanText, " "),

    // 2. Filter for the Aircraft Code
    ExtractCode = List.First(
        List.Select(Words, each 
            let
                // Basic properties
                Txt = _,
                Len = Text.Length(Txt),
                // Check if it contains at least one letter
                HasLetter = Text.Select(Txt, {"A".."Z", "a".."z"}) <> "",
                // Check if it contains at least one digit
                HasDigit = Text.Select(Txt, {"0".."9"}) <> "",
                // Specific exclusion for "Jet2" (which is alphanumeric but an airline)
                IsNotJet2 = Text.Lower(Txt) <> "jet2"
            in
                Len = 4 and 
                HasLetter and 
                HasDigit and 
                IsNotJet2 and
                // Rule: Must NOT be a year starting with 20
                not Text.StartsWith(Txt, "20") and
                // Rule: Must NOT be an ordinal date (17th, 22nd)
                not List.Contains({"th", "st", "nd", "rd"}, Text.End(Text.Lower(Txt), 2))
        )
    )
in
    ExtractCode),
  #"Renamed columns 2" = Table.RenameColumns(#"Inserted Text Between Delimiters 1", {{"Location", "Airline Name"}}),
  #"Added custom 1" = Table.AddColumn(#"Renamed columns 2", "Events", each let
    Source = [headline],
    // Extract everything after the first comma
    Result = Text.Trim(Text.AfterDelimiter(Source, ","))
in
    Result),

  // 1. Remove the suffixes (st, nd, rd, th) from the text so Power Query can recognize the date
  #"Cleaned Date Text" = Table.TransformColumns(#"Added custom 1", {{"date", each Text.Replace(Text.Replace(Text.Replace(Text.Replace(_, "st", ""), "nd", ""), "rd", ""), "th", ""), type text}}),

  #"Final Result" = Table.TransformColumnTypes(#"Cleaned Date Text", {{"date", type date}}, "en-US"),
  #"Removed errors" = Table.RemoveRowsWithErrors(#"Final Result", {"date"}),
  #"Filtered rows" = Table.SelectRows(#"Removed errors", each ([Aircraft Code] <> null)),
  #"Changed column type" = Table.TransformColumnTypes(#"Filtered rows", {{"Airline Name", type text}, {"Aircraft Code", type text}, {"Events", type text}}),
  #"Removed columns 2" = Table.RemoveColumns(#"Changed column type", {"headline"}),
  #"Added index" = Table.AddIndexColumn(#"Removed columns 2", "Index", 1, 1, Int64.Type),
  #"Reordered columns" = Table.ReorderColumns(#"Added index", {"Index", "timestamp", "type", "date", "Airline Name", "Aircraft Code", "Events"}),
  #"Renamed columns 3" = Table.RenameColumns(#"Reordered columns", {{"Index", "EventId"}, {"timestamp", "Timestamp"}, {"type", "Type"}, {"date", "Date"}, {"Airline Name", "AirlineName"}, {"Aircraft Code", "AircraftCode"}})

in
  #"Renamed columns 3";
shared #"Bronze aviationheralddata_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "228ebd15-8b0c-487d-a9f9-d00961af4eea"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "03daaee2-6456-4fe2-9853-752caeb5fb49"]}[Data],
  TableNavigation = Navigation_2{[Id = "Silver_aviationheralddata", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
