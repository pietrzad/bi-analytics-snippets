// ============================================
// Format ALL DAX expressions in the model
// Short Lines format
// ============================================

bool shortFormat = true;
bool skipSpaceAfterFunctionName = false;

// Measures
foreach (var measure in Model.AllMeasures)
{
    FormatDax(measure);
}

// Calculated Columns
foreach (var column in Model.AllColumns.OfType<CalculatedColumn>())
{
    FormatDax(column);
}

// Calculation Items
foreach (var item in Model.AllCalculationItems)
{
    FormatDax(item);
}

// Calculated Tables
foreach (var table in Model.Tables.OfType<CalculatedTable>())
{
    FormatDax(table);
}

// Execute formatter with Short Lines
CallDaxFormatter(
    shortFormat: shortFormat,
    skipSpaceAfterFunctionName: skipSpaceAfterFunctionName
);



