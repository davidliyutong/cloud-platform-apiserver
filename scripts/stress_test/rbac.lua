wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Accept"] = "application/json"
wrk.body = [[{
  "subject": "alice",
  "object": "resources::/groups/",
  "action": "destroy"
}]]

