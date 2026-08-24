// Use this c# code in tabular editor to rename names inside a measure after model refactoring

string oldName = "<string to replace>";
string newName = "<string use for replacing>";

int changedCount = 0;
int totalOccurrences = 0;
var changedMeasures = new System.Collections.Generic.List<string>();

foreach (var m in Model.AllMeasures)
{
    if (m.Expression != null && m.Expression.Contains(oldName))
    {
        // Zlicz wystąpienia przed zamianą
        int occurrences = (m.Expression.Length - m.Expression.Replace(oldName, "").Length) / oldName.Length;
        totalOccurrences += occurrences;

        // Podmień w wyrażeniu DAX
        m.Expression = m.Expression.Replace(oldName, newName);

        changedCount++;
        changedMeasures.Add(string.Format("[{0}].[{1}] ({2}x)", m.Table.Name, m.Name, occurrences));
    }
}

// Podsumowanie
string summary = string.Format(
    "Zamieniono '{0}' -> '{1}'\r\n" +
    "Zmodyfikowanych miar: {2}\r\n" +
    "Łącznie wystąpień: {3}\r\n\r\n" +
    "Zmienione miary:\r\n{4}",
    oldName, newName, changedCount, totalOccurrences,
    string.Join("\r\n", changedMeasures)
);

Info(summary);
