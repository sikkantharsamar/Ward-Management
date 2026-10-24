# Device API (for the hardware team: Harsha, Binura)

## Sending an alert

```
POST  http://<server-ip>:8000/api/alerts/device
Headers:  Content-Type: application/json
          X-Device-Key: <the key of this bed>
Body:     {"source": "bedside_button"}      (or "wearable")
```

Replies:

| Code | Meaning | What the device must do |
|---|---|---|
| 200 | Alert received (this is the ACK). `{"status":"received","alert_id":12,"duplicate":false}` | Stop retrying. Show confirmation (LED). |
| 401 | Unknown device key | Do not retry. Check the key. |
| no reply / timeout / 5xx | Server or network problem | Keep the alert in a buffer, sound the local buzzer, retry every few seconds until ACK. |

`duplicate: true` means the bed already has an open alert; the nurse station is re-sounded, which is fine.

## Rules the firmware must follow (fail-safe design)

1. Debounce the button and never lose a press (use an interrupt).
2. Write every press to the SD card (time, bed, sent/not sent) before sending.
3. Retry until ACK. Never give up silently.
4. If the network is down, sound the local buzzer so staff nearby still know.
5. On battery backup, keep sending alerts and warn when the battery is low.

## Not built yet (agree with the software team)

- Heartbeat: device sends "I am alive, battery X%" every N seconds; the server shows "device offline / low battery".
- Device-to-server encryption (HTTPS/TLS on the microcontroller, or MQTT with TLS).

## Testing without hardware

`python device_simulator/simulate_button.py --key demo-key-bed-1`
