This code renames automatically column names -> _ to space, capitalize each word, leaves id as ID

#"RenameColumns" = Table.TransformColumnNames(
        #"Previous Step",
        (colName as text) =>
            let
                // Replace underscores with spaces
                step1 = Text.Replace(colName, "_", " "),
                
                // Split into words
                words = Text.Split(step1, " "),
                
                // Process each word
                fixedWords = List.Transform(
                    words,
                    (w) =>
                        if Text.Lower(w) = "id" then
                            "ID"
                        else
                            Text.Proper(w)
                ),
                
                // Combine words back into a single string
                result = Text.Combine(fixedWords, " ")
            in
                result
    )
