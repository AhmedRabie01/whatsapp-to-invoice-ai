# n8n Integration Notes

This project uses n8n as the orchestration layer, not as the place where business logic lives.

## Recommended Flow

1. Use a Schedule Trigger node in n8n.
2. Call the FastAPI automation endpoint with an HTTP Request node:

   - Method: `POST`
   - URL: `http://YOUR_SERVER:8000/automation/daily-report`
   - Header: `x-webhook-secret: YOUR_N8N_WEBHOOK_SECRET`
   - JSON body example:

   ```json
   {
     "report_date": "2026-06-11",
     "send_email": false
   }
   ```

3. Optionally branch in n8n to:
   - send a Slack notification
   - send a Telegram message
   - archive the response

## Why This Design

- FastAPI owns report generation and database logic.
- n8n owns scheduling and orchestration.
- This keeps workflow logic in code, where it is easier to test and maintain.

## Useful Endpoints

- `POST /reports/generate`
- `POST /reports/send`
- `POST /automation/daily-report`

## Security

- `/reports/send` requires `x-api-key`
- `/automation/daily-report` requires `x-webhook-secret`
