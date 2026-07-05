
### App Script
```javascript
function sendIciciPdfToBackend() {

  const BACKEND_URL =
    "<Backend URL>";

  const QUERY =
    "from:estatement@icici.bank.in newer_than:365d has:attachment filename:pdf";

  const threads = GmailApp.search(QUERY, 0, 1);

  Logger.log("Found Threads: " + threads.length);

  if (threads.length === 0) {
    Logger.log("No ICICI statement emails found.");
    return;
  }

  for (let i = 0; i < threads.length; i++) {

    const messages = threads[i].getMessages();

    for (let j = 0; j < messages.length; j++) {

      const message = messages[j];

      Logger.log(
        "Processing Email: " + message.getSubject()
      );

      const attachments = message.getAttachments();

      Logger.log(
        "Attachments Found: " + attachments.length
      );

      for (let k = 0; k < attachments.length; k++) {

        const attachment = attachments[k];

        const fileName = attachment.getName();

        const contentType = attachment.getContentType();

        const isPdf =
          contentType === "application/pdf" ||
          fileName.toLowerCase().endsWith(".pdf");

        if (!isPdf) {
          Logger.log("Skipping non-PDF: " + fileName);
          continue;
        }

        Logger.log("PDF Found: " + fileName);

        const payload = {
          file: attachment.copyBlob(),
          email_subject: message.getSubject(),
          email_date: message.getDate().toISOString(),
          gmail_message_id: message.getId()
        };

        const options = {
          method: "post",
          payload: payload,
          muteHttpExceptions: true,
          followRedirects: true
        };

        try {

          Logger.log("Sending PDF to backend...");

          const response = UrlFetchApp.fetch(
            BACKEND_URL,
            options
          );

          const statusCode = response.getResponseCode();

          const responseBody = response.getContentText();

          Logger.log("Status Code: " + statusCode);

          Logger.log("Response Body: " + responseBody);

          if (statusCode >= 200 && statusCode < 300) {

            Logger.log(
              "SUCCESS: PDF sent successfully."
            );

          } else {

            Logger.log(
              "FAILED: Backend returned HTTP " +
              statusCode
            );

          }

        } catch (error) {

          Logger.log(
            "ERROR: " + error.toString()
          );

        }

        // Only send the first PDF during testing.
        return;
      }
    }
  }

  Logger.log("No PDF attachment found.");
}

```


### ENV 

```text

TELEGRAM_BOT_TOKEN=<>
TELEGRAM_CHAT_ID=<>
PDF_PASSWORD=<>

```