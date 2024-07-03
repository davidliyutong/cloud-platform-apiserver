wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Accept"] = "*/*"
wrk.body = [[{
  "username": "test",
  "password": "test",
}]]

