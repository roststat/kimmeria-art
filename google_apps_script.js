function doGet(e) {
  try {
    var sheet = SpreadsheetApp.openById("137KFeMp079ULrLjFXb5y6wzer5iiPtNyirBAHTdsraY").getActiveSheet();

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Дата", "Имя", "Телефон", "Страница", "UTM Source", "UTM Medium", "UTM Campaign", "Реферер"]);
    }

    sheet.appendRow([
      new Date(),
      e.parameter.name || "",
      e.parameter.phone || "",
      e.parameter.event || "",
      e.parameter.utm_source || "",
      e.parameter.utm_medium || "",
      e.parameter.utm_campaign || "",
      e.parameter.referrer || ""
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ result: "ok" }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch(err) {
    return ContentService
      .createTextOutput(JSON.stringify({ result: "error", message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
