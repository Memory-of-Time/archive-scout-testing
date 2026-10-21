Archive Scout v1.2.5: macOS Intel Python 3.11 CI fix

Installation: unzip over the root of the uploaded archive-scout-testing repository,
allowing the tests/unit/test_v125_text_followthrough.py file to be replaced.
Do not create an extra nested directory.

Changed file:
  tests/unit/test_v125_text_followthrough.py

Reason:
  This test incorrectly asserted that server-observed HTTP arrival gaps must
  match a pre-socket pacing reservation. Initial HTTPX connection establishment
  can consume the pacing interval; redirects reuse the established connection.

Updated validation:
  - Still confirms /first, /middle, /last GETs through all available backends.
  - Requires exactly one physical pacing slot per HTTP request.
  - Requires each slot to be separated by at least 12ms with 18ms configured.
  - Confirms each request arrives after its pacing slot.

Production modules and user settings are unchanged. Live Wayback throughput
and macOS Intel 3.11 validation still require an external CI run.
